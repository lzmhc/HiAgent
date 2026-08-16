use std::{env, sync::mpsc::Sender};

use crate::event::AgentEvent;
use eventsource_stream::Eventsource;
use futures_util::StreamExt;
use reqwest::Client;
use serde_json::json;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct AppStatus {
    pub name: String,
    pub model: String,
    pub model_reasoning_effort: String,
    pub workspace: String,
}

#[derive(Debug, Deserialize)]
struct SseEvent {
    role: String,
    content: Option<String>,
    id: Option<String>,
    function: Option<FunctionData>,
    tool_name: Option<String>,
}

#[derive(Debug, Deserialize)]
struct FunctionData {
    name: String,
    arguments: String,
}

fn api_url() -> String {
    String::from("http://127.0.0.1:8000")
}

pub async fn chat(
    message: String,
    tx: Sender<AgentEvent>,
) -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();

    let response = client
        .post(format!("{}/chat", api_url()))
        .json(&json!({
            "messages": message
        }))
        .send()
        .await?;

    let mut stream = response.bytes_stream().eventsource();
    while let Some(event) = stream.next().await {
        let event = event?;

        let data: SseEvent = serde_json::from_str(&event.data)?;

        match data.role.as_str() {
            "content" => {
                tx.send(AgentEvent::Content(data.content.unwrap_or_default()))?;
            }
            "reason" => {
                tx.send(AgentEvent::Reason(data.content.unwrap_or_default()))?;
            }
            "toolCall" => {
                if let Some(func) = data.function {
                    tx.send(AgentEvent::ToolCall {
                        id: data.id.unwrap_or_default(),
                        name: func.name,
                        args: func.arguments,
                    })?;
                }
            }
            "toolResult" => {
                tx.send(AgentEvent::ToolResult {
                    name: data.tool_name.unwrap_or_default(),
                    content: data.content.unwrap_or_default(),
                })?;
            }
            "stop" => {
                tx.send(AgentEvent::Stop)?;
            }
            "error" => {
                tx.send(AgentEvent::Error(data.content.unwrap_or_default()))?;
            }
            other => {
                eprintln!("未知的事件类型: {other}");
            }
        }
    }

    Ok(())
}

pub async fn fetch_status() -> Result<AppStatus, Box<dyn std::error::Error>> {
    let status_url = format!("{}/status", api_url());
    let status = reqwest::get(status_url).await?.json::<AppStatus>().await?;
    Ok(status)
}
