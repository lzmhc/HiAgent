use std::{env, sync::mpsc::Sender};

use crate::agent_event::AgentEvent;
use eventsource_stream::Eventsource;
use futures_util::StreamExt;
use reqwest::Client;
use serde_json::json;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
struct SseEvent {
    #[serde(rename = "type")]
    event_type: String,

    content: Option<String>,
    tool: Option<String>,
    args: Option<serde_json::Value>,
    result: Option<serde_json::Value>,
}

fn api_url() -> String {
    // Overridable backend endpoint (default: local FastAPI chat service).
    env::var("CHAT_API_URL").unwrap_or_else(|_| "http://127.0.0.1:8000/chat".to_string())
}

pub async fn chat(
    message: String,
    tx: Sender<AgentEvent>,
) -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();

    let response = client
        .post(api_url())
        .json(&json!({
            "messages": message
        }))
        .send()
        .await?;

    let mut stream = response.bytes_stream().eventsource();
    while let Some(event) = stream.next().await {
        let event = event?;

        let data: SseEvent = serde_json::from_str(&event.data)?;

        match data.event_type.as_str() {
            "reasoning" => {
                tx.send(AgentEvent::Reasoning(data.content.unwrap_or_default()))?;
            }

            "content" => {
                tx.send(AgentEvent::Content(data.content.unwrap_or_default()))?;
            }

            "finish" => {
                tx.send(AgentEvent::Finish)?;
            }

            "error" => {
                tx.send(AgentEvent::Error(data.content.unwrap_or_default()))?;
            }

            "tool_start" => {
                tx.send(AgentEvent::ToolStart {
                    tool: data.tool.unwrap_or_default(),
                    args: data.args.map(|v| v.to_string()).unwrap_or_default(),
                })?;
            }

            "tool_result" => {
                tx.send(AgentEvent::ToolResult(
                    data.result
                        .map(|v| v.to_string())
                        .or(data.content)
                        .unwrap_or_default(),
                ))?;
            }

            other => {
                eprintln!("[sse] unknown event type: {other}");
            }
        }
    }

    Ok(())
}
