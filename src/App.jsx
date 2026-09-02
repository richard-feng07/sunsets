import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState([])

  useEffect(() => {
    fetch("http://127.0.0.1:5000/prediction").then(
      res => res.json()
    ).then(
      data => {
        setData(data)
      }
    )
  }, [])
  const firstItem = data[0]?.['09/01 07:17 PM'] ?? []
  const days = []
  const score = []
  for(const day of data){
    days.push(Object.keys(day)[0])
    score.push(Object.keys(day)[1])
  }
  console.log(days)

  function Reading({category, value}){
    return (
      <div className='mx-6'>
        <div className='flex my-3 items-center'>
          <div className="size-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FDE68A]"/>
          <h1 className='ml-6'>{category}</h1>
          <h1 className='ml-auto'>{value}</h1>
        </div>
        <div className='length-auto h-px bg-[#3c3c3c] outline-0 mt-1'/>
      </div>
    )
  }

  function DayCard({data}) {
    return (
      <div className='outline-0 outline-transparent shadow-xl/30 w-1/4 h-130 rounded-md mx-6 mt-20 transition duration-300 ease-in-out hover:outline-1 hover:outline-white'>
        <div className='flex justify-between px-4 pt-4'>
          <h1>9/01</h1>
          <h1 className='text-neutral-400'>7:14 PM</h1>
        </div>
        <h1 className='text-6xl font-serif text-amber-200 pt-10 text-shadow-sm/60 text-shadow-amber-100 mb-16'>6/6</h1>
        <Reading category={"cloud cover"} value={"18%"}/>
        <Reading category={"wind speed"} value={"13"}/>
        <Reading category={"humidity"} value={"31%"}/>
      </div>
    )
  }

  return (
    <>
    <div className='mt-20'>
      <h1 className='font-stretch-expanded text-4xl'>Sunsetology</h1>
      <h3 class='mt-2 font-serif'>Know the sky before you look up.</h3>
    </div>
      <ul>
        {firstItem.map(r => (<li>{r.category} : {r.desired} / {r.real}</li>))}
        {days.map(r => (<li>{r}</li>))}
      </ul>

      <div className='flex mt-20 justify-center'>
        <input className='inline-xl px-1 py-2 outline-none border-b border-stone-500 transition duration-300 ease-in-out focus:border-amber-200 text-3xl' placeholder="Irvine, CA"></input>
        <button className='rounded-4xl ml-7 px-8 py-2 bg-amber-200 text-black hover:cursor-pointer shadow-sm shadow-amber-200/50 self-end transition duration-300 ease-in-out hover:bg-amber-300'>Check tonight</button>
      </div>

      <div className='flex justify-center'>
        <DayCard></DayCard>
        <DayCard></DayCard>
        <DayCard></DayCard>
      </div>
    </>
  )
}

export default App
