use std::sync::mpsc::Sender;

use crate::event::{AgentEvent};
use eventsource_stream::Eventsource;
use futures_util::StreamExt;
use reqwest::Client;
use serde_json::{Map, Value, json};

use serde::{Deserialize};

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
    call_id: Option<String>,
    name: Option<String>,
    args: Option<String>,
    completion_tokens: Option<u64>,
    prompt_tokens: Option<u64>,
    total_tokens: Option<u64>
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
            "content" => {
                if let Some(content) = data.content {
                    tx.send(AgentEvent::Content{ content: content });
                }
            }
            "content_delta" => {
                if let Some(content) = data.content {
                    tx.send(AgentEvent::ContentDeltaEvent { content });
                }
            }
            "tool_call" => {
                if let (Some(call_id), Some(name), Some(args)) = (data.call_id, data.name, data.args){
                    tx.send(AgentEvent::ToolCallEvent{ call_id: call_id, name: name, args: args });
                }
            },
            "tool_result" => {
                if let (Some(call_id), Some(content)) = (data.call_id, data.content){
                    tx.send(AgentEvent::ToolResultEvent { call_id: call_id, content: content });
                }
            }
            "stop" => {
                tx.send(AgentEvent::Stop{});
            }
            "error" => {
                if let Some(content) = data.content {
                    tx.send(AgentEvent::Error{content: content})?;
                }
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
                    let content = msg["content"].as_str()?;
                    Some(AgentEvent::User{content: content.to_string()})
                },                                                       
                "content" => {
                    let content = msg["content"].as_str()?;
                    Some(AgentEvent::Content{content: content.to_string()})
                },
                "tool_call" => {
                    let call_id = msg["call_id"].as_str().unwrap_or("").to_string(); 
                    let name = msg["name"].as_str().unwrap_or("").to_string(); 
                    let args = msg["args"].as_str().unwrap_or("").to_string();
                    Some(AgentEvent::ToolCallEvent{ call_id: call_id, name: name, args: args})
                }
                _ => None,                                                                                      
           }                                                                                                   
       }).collect();                                                                                           
    Ok(chunks)
}