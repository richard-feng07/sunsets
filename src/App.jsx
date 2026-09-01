import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [data, setData] = useState({})

  useEffect(() => {
    fetch("http://127.0.0.1:5000/prediction").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
      }
    )
  }, [])
  const firstItem = data[0]?.['05/13 04:55 PM'] ?? []

  return (
    <>
    <div className='mt-20'>
      <h1 className='font-stretch-expanded text-4xl'>Sunsetology</h1>
      <h3 class='mt-2 font-serif'>Know the sky before you look up.</h3>
    </div>
      <ul>
        {firstItem.map(r => (<li>{r.category} : {r.desired} / {r.real}</li>))}
      </ul>

      <div className='flex mt-20 justify-center'>
        <input className='inline-xl px-1 py-2 outline-none border-b border-stone-500 transition duration-300 ease-in-out focus:border-amber-200 text-3xl' placeholder="Irvine, CA"></input>
        <button className='rounded-4xl ml-7 px-8 py-2 bg-amber-200 text-black hover:cursor-pointer shadow-sm shadow-amber-200/50 self-end transition duration-300 ease-in-out hover:bg-amber-300'>Check tonight</button>
      </div>
    </>
  )
}

export default App
