use std::sync::mpsc::Sender;

use crate::event::{AgentEvent};
use eventsource_stream::Eventsource;
use futures_util::StreamExt;
use reqwest::Client;
use serde_json::json;

use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub struct AppStatus {
    pub name: String,
    pub model: String,
    pub model_reasoning_effort: String
}

#[derive(Debug, Deserialize)]
struct SseEvent {
    role: String,
    content: Option<String>,
    tool_call_id: Option<String>,
    function: Option<FunctionData>,
    name: Option<String>,
    completion_tokens: Option<u64>,
    prompt_tokens: Option<u64>,
    total_tokens: Option<u64>
}

#[derive(Debug, Deserialize)]
struct FunctionData {
    name: String,
    arguments: String,
}

#[derive(Debug, Deserialize)]
pub struct SessionInfo {
    pub session_id: String
}

fn api_url() -> String {
    String::from("http://127.0.0.1:8000")
}

pub async fn chat(
    message: String,
    session_id: String,
    tx: Sender<AgentEvent>,
) -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new();

    let response = client
        .post(format!("{}/chat", api_url()))
        .json(&json!({
            "messages": message,
            "session_id": session_id
        }))
        .send()
        .await?;

    let mut stream = response.bytes_stream().eventsource();
    while let Some(event) = stream.next().await {
        let event = event?;

        let data: SseEvent = serde_json::from_str(&event.data)?;

        match data.role.as_str() {
            "assistant" => {
                tx.send(AgentEvent::Assistant{content: data.content.unwrap_or_default()})?;
            }
            "reason" => {
                tx.send(AgentEvent::Reason{ content: data.content.unwrap_or_default()})?;
            }
            "function_call" => {
                if let Some(func) = data.function {
                    tx.send(AgentEvent::ToolCall {
                        id: data.tool_call_id.unwrap_or_default(),
                        name: func.name,
                        args: func.arguments,
                    })?;
                }
            }
            "function_call_output" => {
                tx.send(AgentEvent::ToolResult {
                    tool_call_id: data.tool_call_id.unwrap_or_default(),
                    content: data.content.unwrap_or_default(),
                })?;
            }
            "stop" => {
                tx.send(AgentEvent::Stop)?;
            }
            "error" => {
                tx.send(AgentEvent::Error{content: data.content.unwrap_or_default()})?;
            }
            "token" => {
                tx.send(AgentEvent::Token { 
                    completion_tokens: data.completion_tokens.unwrap_or_default(), 
                    prompt_tokens: data.prompt_tokens.unwrap_or_default(), 
                    total_tokens: data.total_tokens.unwrap_or_default() 
                })?
            }
            _ => {
               eprintln!("unknown role!");
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

pub async fn start_new_session() -> Result<String, Box<dyn std::error::Error>> {
    let session_url = format!("{}/session/new", api_url());
    let response = reqwest::Client::new()
        .post(session_url)
        .send()
        .await?;
    let session_data: serde_json::Value = response.json().await?;
    let session_id = session_data["session_id"].as_str().unwrap().to_string();
    Ok(session_id)
}

pub async fn fetch_sessions() -> Result<Vec<SessionInfo>, Box<dyn std::error::Error>> {
    let url = format!("{}/sessions", api_url());
    let response = reqwest::get(url).await?.json::<serde_json::Value>().await?;
    let sessions: Vec<SessionInfo> = serde_json::from_value(response["sessions"].clone())?;
    Ok(sessions)
}

pub async fn fetch_session_history(session_id: String) -> Result<Vec<AgentEvent>, Box<dyn std::error::Error>> {
    let url = format!("{}/session/{}/history", api_url(), session_id);
    let response = reqwest::get(url).await?.json::<serde_json::Value>().await?;
    let history: Vec<serde_json::Value> = serde_json::from_value(response["history"].clone())?;
    let chunks: Vec<AgentEvent> = history.iter().filter_map(|msg| {                                          
           let role = msg["role"].as_str()?;
           match role {                                                                                        
                "user" => {
                    let content = msg["content"][0]["text"].as_str().unwrap_or("").to_string();  
                    Some(AgentEvent::User{content})
                },                                                       
                "assistant" => {
                    let content = msg["content"][0]["text"].as_str().unwrap_or("").to_string();  
                    Some(AgentEvent::Assistant{content})
                },
                "reason" => {
                    let content = msg["content"][0]["text"].as_str().unwrap_or("").to_string(); 
                    Some(AgentEvent::Reason { content })
                },
                "function_call" => {
                    let id = msg["id"].as_str().unwrap_or("").to_string(); 
                    let func = msg["function"].as_object(); 
                    let name = func
                        .and_then(|f| f.get("name"))
                        .and_then(|v| v.as_str())
                        .unwrap_or("")
                        .to_string();
                    let args = func
                        .and_then(|f| f.get("arguments"))
                        .and_then(|v| v.as_str())
                        .unwrap_or("")
                        .to_string();
                    Some(AgentEvent::ToolCall { id, name, args })
                }
                _ => None,                                                                                      
           }                                                                                                   
       }).collect();                                                                                           
    Ok(chunks)
}