import './App.css'
import { useEffect, useState, useRef } from "react"
import Button from "react-bootstrap/Button"
import Table from "react-bootstrap/Table"

type CustomUser = {
  id: number;
  name: string;
  email: string;
  password: string;
}

type EmailLetter = {
  sender: number;
  topic: string;
  date_sent: string;
  date_received: string;
  text: string;
  files: string[];
}

function MessageComponent({ sender, topic, date_sent, date_received, text, files }: EmailLetter) {
  return (
    <tr>
      <td>{sender}</td>
      <td>{topic}</td>
      <td>{date_sent}</td>
      <td>{date_received}</td>
      <td>{text}</td>
      <td>
        {files?.map(file => (<a href={file}>{file}</a>))}
      </td>
    </tr>
  );
}

export default function App() {
  const [messages, setMessages] = useState<EmailLetter[]>([])
  const [progress, setProgress] = useState(0)
  const socket = useRef<WebSocket | null>(null)

  useEffect(() => {
    const url = "ws://127.0.0.1:8000/ws/email_letters/"
    socket.current = new WebSocket(url)

    socket.current.onopen = () => {
      console.log("Connection opened")
    };

    socket.current.onclose = (event) => {
      console.error("WebSocket connection closed:", event.reason)
      if (event.code !== 1000) {
        console.error(`WebSocket closed with code ${event.code}`)
      }
    };

    socket.current.onerror = (error) => {
      console.error("WebSocket error:", error)
    };

    socket.current.onmessage = (event) => {
      try {
        const { data, progress } = JSON.parse(event.data)
        setMessages(prevMessages => [...(progress === 100 ? prevMessages : []), ...data])
        setProgress(progress);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }

  }, []);

  const handleGetMessages = () => {
    if (socket.current) {
      socket.current.send("start")
    } else {
      console.error("WebSocket is not initialized");
    }
  };

  return (
    <>
      <div>Progress: {progress}%</div>
      <Button onClick={handleGetMessages}>Get Messages</Button>
      <Table responsive>
        <thead>
            <tr>
              <td>sender.id</td>
              <td>topic</td>
              <td>date_sent</td>
              <td>date_received</td>
              <td>text</td>
              <td>files</td>
            </tr>
        </thead>
        <tbody>
        {messages.map((message, index) => (
            <MessageComponent key={index} {...message} />
        ))}
        </tbody>
      </Table>
    </>
  );
}
