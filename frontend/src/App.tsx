import './App.css'
import { useEffect, useState, useRef } from "react"
import Button from "react-bootstrap/Button"
import Table from "react-bootstrap/Table"
import ProgressBar from "react-bootstrap/ProgressBar"

// type CustomUser = {
//   id: number;
//   name: string;
//   email: string;
//   password: string;
// }

type EmailLetterFile = {
  email_letter: number;
  file: string;

}

type EmailLetter = {
  sender: number;
  topic: string;
  date_sent: string;
  date_received: string;
  text: string;
  files: EmailLetterFile[];
}


function MessageComponent({ sender, topic, date_sent, date_received, text, files }: EmailLetter) {
  console.log("!!!", files)
  return (
    <tr>
      <td>{sender}</td>
      <td>{topic}</td>
      <td>{date_sent}</td>
      <td>{date_received}</td>
      <td>{text}</td>
      <td>
        {files?.map((file, index) => <a key={index} href={`http://127.0.0.1:8000${file.file}/`} download>{file.file}</a>)}
      </td>
    </tr>
  );
}

function ProgressComponent({ progress }: { progress: number }) {
  function getLabel() {
    if (progress <= 0) {
      return "Сообщения не получены"
    }
    else if (progress < 100) {
      return "Получение сообщений"
    }
    else {
      return "Сообщения получены"
    }
  }
  return (
      <>
        <h5>{getLabel()}</h5>
        <ProgressBar now={progress} label={`${progress}%`}/>
      </>
  )
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
        console.log(data.files)
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
      <ProgressComponent progress={progress} />
      <Button className={"my-3"} onClick={handleGetMessages}>Get Messages</Button>
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
