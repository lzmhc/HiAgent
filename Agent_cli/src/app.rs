use ratatui::widgets::{ListState, ScrollbarState};

use crate::{api::{AppStatus, SessionInfo}, event::{AgentEvent, ChatChunk}};

pub struct App {
    pub current_session_id: String,

    pub input: String,

    pub blocks: Vec<ChatChunk>,

    pub scroll: u16,

    pub scrollbar: ScrollbarState,

    pub status: Option<AppStatus>,

    pub show_reasoning: bool,

    pub show_session_popup: bool,                                              
    
    pub sessions: Vec<SessionInfo>,                                            
    
    pub session_list_state: ListState,
}

impl App {
    pub fn new() -> Self {
        Self {
            current_session_id: String::new(),
            input: String::new(),
            blocks: Vec::new(),
            scroll: 0,
            scrollbar: ScrollbarState::default(),
            status: None,
            show_reasoning: true,
            show_session_popup: false,
            sessions: Vec::new(),
            session_list_state: ListState::default(),
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

    pub fn toggle_session(&mut self) {
        self.show_session_popup = !self.show_session_popup;
        if !self.show_session_popup {
            self.session_list_state.select(None);
        }
    }

    pub fn session_list_next(&mut self) {
        if self.sessions.is_empty() { return; }
        let i = match self.session_list_state.selected() {
            Some(i) => (i+1)%self.sessions.len(),
            None => 0,
        };
        self.session_list_state.select(Some(i));
    }

    pub fn session_list_prev(&mut self) {
        if self.sessions.is_empty() { return; }
        let i = match self.session_list_state.selected() {
            Some(i) => {
                if i==0 { self.sessions.len() - 1 } else { i - 1 }
            }
            None => 0,
        };
        self.session_list_state.select(Some(i));
    }

    pub fn select_current_session(&mut self) -> Option<String> {
        if let Some(i) = self.session_list_state.selected() {
            if let Some(session) = self.sessions.get(i) {
                let session_id = session.session_id.clone();
                self.current_session_id = session_id.clone();
                self.blocks.clear();
                self.scroll = 0;
                self.show_session_popup = false;
                return Some(session_id)
            }
        }
        None
    }

    pub fn close_session_popup(&mut self) {
        self.show_session_popup = false;
        self.session_list_state.select(None);
    }

    pub fn update_sessions(&mut self, sessions: Vec<SessionInfo>) {
        self.sessions = sessions;
        if !self.sessions.is_empty() {
            self.session_list_state.select(Some(0));
        } else {
            self.session_list_state.select(None);
        }
    }
}
