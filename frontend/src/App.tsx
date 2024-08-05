import './App.css'
import {useEffect, useState} from "react";

type CustomUser = {
  id: number,
  name: string,
  email: string,
  password: string,
}

type EmailLetter = {
  sender: CustomUser,
  topic: string,
  date_sent: string,
  date_received: string,
  text: string
}

function MessageComponent(message: EmailLetter) {
  return (
    <div>
      <h5>{message.topic}</h5>
      {message.sender?.name}({message.date_sent}): {message.text}
    </div>
  )
}
export default function App() {
  const [messages, setMessages] = useState<EmailLetter[]>([]);
  let socket: WebSocket | null = null;
  useEffect(() => {
    socket = new WebSocket("ws://127.0.0.1:8000/ws/email_letters/")
    socket.onopen = () => { console.log("Connection opened") }
    socket.onclose = () => { console.log("Connection closed") }
    socket.onmessage  = (event) => { setMessages([...(JSON.parse(event.data).data)]) }
    return () => {
      socket?.close()
    }
  }, [messages, setMessages])

  return (
    <>
      <button onClick={() => socket?.send("start")}>Get Messages</button>
      {messages.map((message, index) => {
        return (
            <MessageComponent key={`message_component-${index}`} {...message} />
        )
      })}
    </>
  )
}
