import './App.css'
import {useState, useEffect, useRef} from "react"
import Button from "react-bootstrap/Button"
import Table from "react-bootstrap/Table"
import ProgressBar from "react-bootstrap/ProgressBar"
import Form from "react-bootstrap/Form"


type CustomUser = {
  id: number,
  username: string,
  email: string;
  password: string;
}

type EmailLetterFile = {
  email_letter: number;
  file: string;
  name: string
}

type EmailLetter = {
  id: number;
  sender: number;
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
      <td>{text}</td>
      <td>
        {files?.map((file, index) => <a key={index} href={`http://127.0.0.1:8000${file.file}/`} download>{file.name}</a>)}
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
  const [isAuthenticated, setIsAuthenticated ] = useState(false)
  const [messages, setMessages] = useState<EmailLetter[]>([])
  const [progress, setProgress] = useState(0)
  const socket = useRef<WebSocket | null>(null)
  const [csrf, setCsrf] = useState<string>("")
  const [userData, setUserData] = useState<CustomUser | null>(null)

  useEffect(() => {
    async function fetchCsrf(){
      const resp = await fetch("http://127.0.0.1:8000/api/csrf/")
      setCsrf((await resp.json()).csrf_token)
    }
    fetchCsrf()
  }, [])

  function createWebsocket() {
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
      socket.current = new WebSocket(url)
    };

    socket.current.onerror = (error) => {
      console.error("WebSocket error:", error)
    };

    socket.current.onmessage = (event) => {
      try {
        const { data, progress } = JSON.parse(event.data)
        setMessages(prevMessages => [...prevMessages, ...data])
        setProgress(progress);
      } catch (error) {
        console.error("Error parsing WebSocket message:", error)
      }
    }
  }

  useEffect(() => {
    createWebsocket()
  }, [userData]);

  const handleGetMessages = () => {
    if (socket.current) {
      socket.current.send("start")
    } else {
      console.error("WebSocket is not initialized");
    }
  };
  async function sendMessageForm() {
    const formData = new FormData()
    const date = new Date()
    formData.append("topic", (document.querySelector("#topic_input") as HTMLInputElement).value)
    formData.append("text", (document.querySelector("#text_input") as HTMLInputElement).value)
    formData.append("date_sent", `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDay()}`)
    formData.append("sender", userData ? userData.id.toString() : "")
    const resp = await fetch("http://127.0.0.1:8000/api/email/letters/", {
      method: "POST",
      body: formData
    })
    if (resp.status === 201) {
      console.log("Message sent")
      const newLetter: EmailLetter = await resp.json()
      const fileList = (document.querySelector("#file_input") as HTMLInputElement).files
      if (fileList) {
        Array.from(fileList).forEach((file) => {
          const fileFormData = new FormData()
          fileFormData.append("file", file)
          fileFormData.append("email_letter", newLetter.id.toString())
          fetch("http://127.0.0.1:8000/api/email/files/", {
            method: "POST",
            body: fileFormData,
          })
        })
      }
    }
    else {
      console.log("Message not sent")
    }
  }

  async function handleLogin() {
    const email = (document.querySelector("#user_email_input") as HTMLInputElement).value;
    const password = (document.querySelector("#user_password_input") as HTMLInputElement).value;

    const csrftoken = csrf // Function to get CSRF token from cookies

    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/auth/login/", {
        method: "POST",
        headers: {
          'X-CSRFToken': csrftoken,  // Include CSRF token here
        },
        credentials: "include",
        body: formData,  // Send FormData object
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Error ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      if (response.status === 200) {
        setIsAuthenticated(true)
        setUserData(data.user)
        console.log(data)
      }
    } catch (error) {
      console.error('There was a problem with your fetch operation:', error);
    }
  }

  return isAuthenticated ?  (
    <>
      {userData && <h1>{userData?.id} - {userData?.email}</h1>}
      <Form>
        <Form.Control id={"topic_input"} placeholder={"Topic"} className={"mb-1"}></Form.Control>
        <Form.Control id={"text_input"} placeholder={"Text"} type={"text"} as={"textarea"} rows={3} className={"mb-1"}></Form.Control>
        <Form.Control id={"file_input"} className={"mb-3"} type={"file"} multiple></Form.Control>
        <Button onClick={sendMessageForm}>Send Message</Button>
      </Form>
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
  ) : (
      <>
        <Form style={{maxWidth: "300px", margin: "auto"}}>
          <Form.Control id={"user_email_input"} className={"mb-1"} type={"email"}></Form.Control>
          <Form.Control id={"user_password_input"} className={"mb-1"} type={"password"}></Form.Control>
          <Button onClick={handleLogin}>Log In</Button>
        </Form>
      </>
  )
}
