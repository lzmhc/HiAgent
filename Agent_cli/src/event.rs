use crate::api::ContentValue;

#[derive(Debug)]
pub enum AgentEvent {
    System {
        content: ContentValue
    },
    User {
        content: ContentValue,
    },
    Assistant {
        content: ContentValue,
    },
    Tool {
        tool_call_id: String,
        name: String,
        content: ContentValue
    },
    Stop,
    Error {
        content: ContentValue,
    },
    Token {
        completion_tokens: u64,
        prompt_tokens: u64,
        total_tokens: u64,
    }
}