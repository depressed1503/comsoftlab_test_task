import './App.css'
import {useState, useEffect, useRef, useCallback} from "react"
import Button from "react-bootstrap/Button"
import Table from "react-bootstrap/Table"
import ProgressBar from "react-bootstrap/ProgressBar"
import Form from "react-bootstrap/Form"

type CustomUser = {
  id: number;
  username: string;
  email: string;
  password: string;
}

type EmailLetterFile = {
  email_letter: number;
  file: string;
  name: string;
}

type EmailLetter = {
  id: number;
  sender: string;
  topic: string;
  date_sent: string;
  date_received: string;
  text: string;
  files: EmailLetterFile[];
}

function MessageComponent({ sender, topic, date_sent, date_received, text, files }: EmailLetter) {
  return (
    <tr>
      <td>{sender}</td>
      <td>{topic}</td>
      <td>{date_sent}</td>
      <td>{date_received}</td>
      <td>{text.slice(0, 100)}</td>
      <td>
        {files?.map((file, index) => (
          <a key={index} href={`http://127.0.0.1:8000${file.file}/`} download>{file.name}</a>
        ))}
      </td>
    </tr>
  );
}

function ProgressComponent({ progress, max, text }: { progress: number, max: number, text: string }) {
  return (
    <>
      <h5>{text}</h5>
      <ProgressBar now={progress === -1 ? 100 :(progress / max) * 100} label={progress === -1 ? "100%" : `${Math.round((progress / max) * 100)}%`} />
    </>
  )
}

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [messages, setMessages] = useState<EmailLetter[]>([])
  const [progressBarText, setProgressBarText] = useState<string>("Сообщения не получены, нажмите кнопку")
  const [progress, setProgress] = useState(-1)
  const [progressMax, setProgressMax] = useState(1)
  const socket = useRef<WebSocket | null>(null)
  const [csrf, setCsrf] = useState<string>("")
  const [userData, setUserData] = useState<CustomUser | null>(null)

  useEffect(() => {
    async function fetchCsrf() {
      const resp = await fetch("http://127.0.0.1:8000/api/csrf/")
      setCsrf((await resp.json()).csrf_token)
    }
    fetchCsrf()
  }, [])

  const createWebSocket = useCallback(() => {
    const url = `ws://127.0.0.1:8000/ws/email_letters/?username=${userData?.username}&password=${userData?.password}`
    socket.current = new WebSocket(url)

    socket.current.onopen = () => {
      console.log("WebSocket Connected")
    };

    socket.current.onclose = (event) => {
       console.log('WebSocket connection closed with code', event.code);
        if (event.code === 1006) {
            console.warn('Connection closed abnormally. Reconnecting...');
            setTimeout(() => {
              socket.current = new WebSocket(url);
            }, 1000);
        }
    };

    socket.current.onerror = (error) => {
      console.error("WebSocket error:", error)
    };

    socket.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log(data)
        if (data.progress !== undefined && data.max !== undefined) {
          setProgressBarText(`Идет чтение сообщений: ${data.progress + 1}`)
          setProgressMax(data.max)
        }

        if(data.data !== undefined) {
          setMessages(messages => [...messages, data.data].filter((value, index, array) => array.indexOf(value) === index))
        }

        if(data.reverse_progress !== undefined) {
          console.log("Reverse progress:", data.reverse_progress)
          setProgressBarText(`Идет получение сообщений ${data.reverse_progress}`)
          setProgress(data.reverse_progress)
        }

      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }
  }, [userData, messages, progress, setMessages])

  useEffect(() => {
    createWebSocket()
  }, [userData, createWebSocket, messages]);

  const handleGetMessages = () => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN)  {
      socket.current.send("start")
    } else {
      console.error("WebSocket is not initialized");
    }
  };

  async function handleLogin() {
    const email = (document.querySelector("#user_email_input") as HTMLInputElement).value;
    const password = (document.querySelector("#user_password_input") as HTMLInputElement).value;

    const csrftoken = csrf

    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        headers: {
          'X-CSRFToken': csrftoken,
        },
        credentials: "include",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      if (response.status === 200) {
        setIsAuthenticated(true)
        setUserData(data.user)
      }
    } catch (error) {
      console.error('There was a problem with your fetch operation:', error);
    }
  }

  return isAuthenticated ? (
    <>
      {userData && <h1>{userData?.id} - {userData?.email}</h1>}
      <ProgressComponent max={progressMax} text={progressBarText} progress={progress} />
      <Button className={"my-3"} onClick={handleGetMessages}>Get Messages</Button>
      <Table responsive>
        <thead>
          <tr>
            <th>Sender</th>
            <th>Topic</th>
            <th>Date Sent</th>
            <th>Date Received</th>
            <th>Text</th>
            <th>Files</th>
          </tr>
        </thead>
        <tbody>
          {messages.map((message) => (
            <MessageComponent key={message.id} {...message} />
          ))}
        </tbody>
      </Table>
    </>
  ) : (
    <>
      <Form style={{ maxWidth: "300px", margin: "auto" }}>
        <Form.Control id={"user_email_input"} className={"mb-1"} type={"email"} placeholder="Email" />
        <Form.Control id={"user_password_input"} className={"mb-1"} type={"password"} placeholder="Password" />
        <Button onClick={handleLogin}>Log In</Button>
      </Form>
    </>
  )
}
