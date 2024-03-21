use std::io::{Read, Write, Error};
use std::net::TcpStream;
use std::sync::Mutex;

fn recv(socket: &mut TcpStream, message_length: usize) -> Result<Vec<u8>, Error> {
    let lock = Mutex::new(());
    let _guard = lock.lock().unwrap();
    let mut message = vec![0; message_length];
    let mut total_read = 0;

    while total_read < message_length {
        match socket.read(&mut message[total_read..]) {
            Ok(n) => {
                if n == 0 {
                    eprintln!("ERROR: recv: Socket connection broken, returning None!");
                    return Err(std::io::Error::new(std::io::ErrorKind::BrokenPipe, "Socket connection broken"));
                } else {
                    total_read += n;
                }
            },
            Err(e) => {
                eprintln!("ERROR: recv: Socket connection broken, returning None!");
                return Err(e);
            }
        }
    }

    Ok(message)
}

fn send(socket: &mut TcpStream, message: &[u8]) -> Result<usize, Error> {
    let lock = Mutex::new(());
    let _guard = lock.lock().unwrap();
    let message_length = message.len();
    let mut total_sent = 0;

    while total_sent < message_length {
        match socket.write(&message[total_sent..]) {
            Ok(n) => {
                if n == 0 {
                    eprintln!("ERROR: send: Socket connection broken, returning None!");
                    return Err(std::io::Error::new(std::io::ErrorKind::BrokenPipe, "Socket connection broken"));
                } else {
                    total_sent += n;
                }
            },
            Err(e) => {
                eprintln!("ERROR: send: Socket connection broken, returning None!");
                return Err(e);
            }
        }
    }

    Ok(total_sent)
}