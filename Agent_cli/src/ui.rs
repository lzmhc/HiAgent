use std::format;

use crate::event::AgentEvent;
use crate::{app::App};
use ratatui::style::Stylize;
use ratatui::{layout::Rect, widgets::ListItem};
use ratatui::widgets::{Clear, HighlightSpacing, List, Wrap};
use unicode_width::UnicodeWidthChar;
use ratatui::{
    Frame,
    layout::{Constraint, Direction, Layout},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, Borders, Paragraph, Scrollbar, ScrollbarOrientation},
};

pub fn draw(frame: &mut Frame, app: &mut App) {
    let layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(2), // Header
            Constraint::Min(1),    // Chat
            Constraint::Length(3), // Input
            Constraint::Length(1), // Footer
        ])
        .split(frame.area());

    draw_header(frame, layout[0], app);

    draw_chat(frame, layout[1], app);

    draw_input(frame, layout[2], app);

    draw_footer(frame, layout[3]);

    if app.show_session_popup {
        draw_session_popup(frame, frame.area(), app)
    }
}

fn draw_header(frame: &mut Frame, area: ratatui::layout::Rect, app: &App) {
    let title = if let Some(status) = &app.status {
        format!(
            "{}  Model:{}  Reason:{} ",
            status.name, status.model, status.model_reasoning_effort
        )
    } else {
        "Loading...".to_string()
    };
    let header = Paragraph::new(title)
        .style(
            Style::default()
                .fg(Color::LightGreen)
                .add_modifier(Modifier::BOLD),
        )
        .block(Block::default().borders(Borders::BOTTOM));
    frame.render_widget(header, area);
}

fn draw_chat(frame: &mut Frame, area: Rect, app: &mut App) {
    let mut text = Text::default();
    let mut delta = true;
    for block in &app.blocks {
        match block {
            AgentEvent::User{content} => {
                text.lines.push(Line::from(vec![
                    Span::styled("▸ ", Style::default().fg(Color::White)),
                    Span::styled(content, Style::default().fg(Color::White))
                ]));
                delta = true;
                true
            }

            AgentEvent::Content{ content } => {
                text.lines.push(Line::from(vec![
                    Span::styled("▹ ", Style::default().fg(Color::Cyan)),
                    Span::styled(content, Style::default().fg(Color::Cyan))
                ]));
                true
            }

            AgentEvent::ContentDeltaEvent{ content } => {
                if delta{
                    text.lines.push(Line::default());
                    text.push_span(Span::from(
                        Span::styled("▹ ", Style::default().fg(Color::Cyan))
                    ));
                    delta = false;
                }
                text.push_span(Span::from(
                    Span::styled(content, Style::default().fg(Color::Cyan))
                ));
                true
            }

            AgentEvent::ToolCallEvent{ call_id, name, args } => {
                text.lines.push(Line::from(vec![
                    Span::styled(format!("🛠 {name}({args})"), Style::default().fg(Color::Yellow))
                ]));
                delta = true;
                true
            }

            AgentEvent::ToolResultEvent{ call_id, content } => {
                text.lines.push(Line::from(vec![
                    Span::styled(format!("⚡ {content}"), Style::default().fg(Color::Green))
                ]));
                delta = true;
                true
            }

            AgentEvent::Error{content} => {
                text.lines.push(Line::from(vec![
                    Span::styled("Error: ", Style::default().fg(Color::Red)),
                    Span::styled(content, Style::default().fg(Color::Red))
                ]));
                delta = true;
                true
            }

            AgentEvent::Token { completion_tokens, prompt_tokens, total_tokens } => {
                let s = format!("(⇑{}⇓{}➣{})", completion_tokens, prompt_tokens, total_tokens);
                text.push_span(Span::from(
                    Span::styled(s, Style::default().fg(Color::DarkGray))
                ));
                delta = true;
                true
            }

            AgentEvent::Stop{} => {
                true
            }

            _ => {
                false
            }
        };
    }

    let chat = Paragraph::new(text)
        .scroll((app.scroll, 0))
        .wrap(Wrap { trim: false });
    frame.render_widget(chat, area);
    let scrollbar = Scrollbar::new(ScrollbarOrientation::VerticalRight);
    frame.render_stateful_widget(scrollbar, area, &mut app.scrollbar);
}

fn draw_input(frame: &mut Frame, area: Rect, app: &App) {
    let block = Block::default()
        .style(Style::default()
            .bg(Color::Black)
            .fg(Color::Green)
        );
    let input_text = app.input.as_str().to_string();
    let input = Paragraph::new(input_text)
        .wrap(Wrap { trim: false })
        .block(block.clone());
    let inner_area = block.inner(area);
    let cursor_x = inner_area.x + app.input.chars()
        .map(|c| c.width().unwrap_or(0) as u16)
        .sum::<u16>();
    let cursor_y = inner_area.y;
    frame.render_widget(input, area);
    frame.set_cursor_position((cursor_x, cursor_y));
}

fn draw_footer(frame: &mut Frame, area: ratatui::layout::Rect) {
    let footer = Paragraph::new(" Ctrl+L:Session Ctrl+R:Reasoning Ctrl+C:Exit ")
        .style(Style::default()
            .bg(Color::DarkGray)
        );

    frame.render_widget(footer, area);
}

fn draw_session_popup(frame: &mut Frame, _area: Rect, app: &mut App) {
    let area = frame.area();
    let popup_area = area.centered(
        Constraint::Percentage(60), 
        Constraint::Percentage(50)
    );
    
    let items: Vec<ListItem> = app
        .sessions
        .iter()
        .map(|s| {                                                                                                                                       
            ListItem::new(Line::from(format!("{}", &s.session_id)))    
        })
        .collect();
    let list = List::new(items)                                                                                                                                   
           .block(                                                                                                                                                   
               Block::default()                                                                                                                                     
                   .title(" Session List ")
                   .bg(Color::DarkGray)
                   .fg(Color::Cyan)
           )                                                                                                                                                         
           .highlight_style(Style::default().bg(Color::DarkGray).add_modifier(Modifier::BOLD))                                                                       
           .highlight_symbol(" ▸ ")                                                                                                                                  
           .highlight_spacing(HighlightSpacing::Always);                                                                                                             
    frame.render_widget(Clear, popup_area);
    frame.render_stateful_widget(list, popup_area, &mut app.session_list_state);
}