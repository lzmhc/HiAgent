use ratatui::widgets::ScrollbarState;

use crate::{api::AppStatus, event::{AgentEvent, ChatChunk}};

pub struct App {
    pub input: String,

    pub blocks: Vec<ChatChunk>,

    pub scroll: u16,

    pub scrollbar: ScrollbarState,

    pub status: Option<AppStatus>,

    pub show_reasoning: bool,
}

impl App {
    pub fn new() -> Self {
        Self {
            input: String::new(),
            blocks: Vec::new(),
            scroll: 0,
            scrollbar: ScrollbarState::default(),
            status: None,
            show_reasoning: true,
        }
    }

    pub fn toggle_reasoning(&mut self) {
        self.show_reasoning = !self.show_reasoning;
    }
    pub fn insert_char(&mut self, c: char) {
        self.input.push(c);
    }

    pub fn backspace(&mut self) {
        self.input.pop();
    }

    pub fn clear(&mut self) {
        self.input.clear();
    }

    pub fn handle_agent_event(&mut self, event: AgentEvent) {
        match event {
            AgentEvent::Content(text) => match self.blocks.last_mut() {
                Some(ChatChunk::Assistant(s)) => {
                    s.push_str(&text);
                }
                _ => {
                    self.blocks.push(ChatChunk::Assistant(text));
                }
            },

            AgentEvent::Reason(text) => match self.blocks.last_mut() {
                Some(ChatChunk::Reasoning(s)) => {
                    s.push_str(&text);
                }
                _ => {
                    self.blocks.push(ChatChunk::Reasoning(text));
                }
            },
            AgentEvent::ToolCall { id: _, name, args } => {
                self.blocks.push(ChatChunk::ToolCall { name, args });
            }

            AgentEvent::ToolResult { name, content } => {
                self.blocks.push(ChatChunk::ToolResult { name, content });
            }

            AgentEvent::Error(err) => {
                self.blocks.push(ChatChunk::Error(err));
            }

            AgentEvent::Stop => {}
        }
    }
}
