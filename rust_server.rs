use std::net::{TcpListener, TcpStream};
use std::thread;
use std::io::prelude::*;
use std::collections::HashMap;

struct Server {
    names: HashMap<String, String>,
    sockets: HashMap<String, TcpStream>,
}

impl Server {
    fn new() -> Server {
        Server {
            names: HashMap::new(),
            sockets: HashMap::new(),
        }
    }

    fn cleanup_client(&mut self, stream: TcpStream) {
        // Implement cleanup logic here
    }

    fn handle_client(&mut self, mut stream: TcpStream) {
        let mut buffer = [0; 1024];
        stream.read(&mut buffer).unwrap();

        let request = String::from_utf8_lossy(&buffer[..]);
        // Implement request handling logic here

        self.cleanup_client(stream);
    }

    fn main(&self) {
        let listener = TcpListener::bind("127.0.0.1:7878").unwrap();

        for stream in listener.incoming() {
            let stream = stream.unwrap();

            thread::spawn(|| {
                self.handle_client(stream);
            });
        }
    }
}

fn main() {
    let server = Server::new();
    server.main();
}