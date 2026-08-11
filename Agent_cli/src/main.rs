mod app;
mod ui;
mod agent_event;
mod api;

use std::{
    io,
    sync::mpsc,
    time::{Duration}
};
use crossterm::{
    event::{self, Event, KeyCode, KeyModifiers},
    execute,
    terminal::{
        disable_raw_mode, enable_raw_mode,
        EnterAlternateScreen, LeaveAlternateScreen,
    },
};
use ratatui::{
    backend::CrosstermBackend,
    Terminal,
};
use crate::agent_event::{AgentEvent, ChatChunk};
use app::App;


fn main() -> Result<(), io::Error> {
    enable_raw_mode()?;

    let mut stdout = io::stdout();

    execute!(stdout, EnterAlternateScreen)?;

    let backend = CrosstermBackend::new(stdout);

    let mut terminal = Terminal::new(backend)?;

    let mut app = App::new();

    let (tx, rx) = mpsc::channel::<AgentEvent>();
    loop {
        while let Ok(event) = rx.try_recv() {
            app.handle_agent_event(event);
        }
        terminal.draw(|f| {
            ui::draw(f, &mut app);
        })?;
        if event::poll(Duration::from_millis(16))? {
            if let Event::Key(key) = event::read()? {
                match key.code {
                    // ctrl+q 退出
                    KeyCode::Char('q')
                        if key.modifiers.contains(KeyModifiers::CONTROL) =>
                    {
                        break;
                    }

                    KeyCode::Char(c) => {
                        app.insert_char(c);
                    }

                    KeyCode::Backspace => {
                        app.backspace();
                    }

                    KeyCode::Enter => {
                        let prompt = app.input.clone();
                        if prompt.trim().is_empty() {
                            continue;
                        }
                        app.blocks.push(ChatChunk::User(prompt.clone()));
                        let tx = tx.clone();
                        std::thread::spawn(move || {
                            let rt = tokio::runtime::Runtime::new().unwrap();
                            rt.block_on(async {
                                if let Err(e) = api::chat(prompt, tx).await {
                                    eprintln!("{e}");
                                }
                            });
                        });
                        app.clear();
                    }
                    KeyCode::Up => {
                        app.scroll = app.scroll.saturating_sub(1);
                    }

                    KeyCode::Down => {
                        app.scroll += 1;

                        app.scrollbar = app
                            .scrollbar
                            .position(app.scroll as usize);
                    }
                    KeyCode::Esc => {
                        app.clear();
                    }

                    _ => {}
                }
            }
        }
    }

    disable_raw_mode()?;

    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen
    )?;

    terminal.show_cursor()?;

    Ok(())
}