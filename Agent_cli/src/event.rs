#[derive(Debug)]
pub enum AgentEvent {
    User {
        content: String,
    },
    Content {
        content: String,
    },
    ContentDeltaEvent{
        content: String,
    },
    ToolCallEvent {
        call_id: String,
        name: String,
        args: String
    },
    ToolResultEvent {
        call_id: String,
        content: String
    },
    Stop {},
    Error {
        content: String,
    },
    Token {
        completion_tokens: u64,
        prompt_tokens: u64,
        total_tokens: u64,
    }
}