import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState([])
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // useEffect(() => {
  //   fetch("http://127.0.0.1:5000/prediction").then(
  //     res => res.json()
  //   ).then(
  //     data => {
  //       setData(data)
  //     }
  //   )
  // }, [])

  function Reading({category, value, unit, met}){
    return (
      <div className='mx-6'>
        <div className='flex my-3 items-center'>
          {met ? <div className="size-2 rounded-full bg-amber-200 shadow-[0_0_8px_#FDE68A]"/> : <div className="size-2 rounded-full outline-1 outline-[#3c3c3c]"/> }
          <h1 className={`ml-6 ${met ? "text-white" : "text-[#767676]"}`}>{category}</h1>
          <h1 className={`ml-auto ${met ? "text-white" : "text-[#767676]"}`}>{value} {unit}</h1>
        </div>
        <div className='length-auto h-px bg-[#3c3c3c] outline-0 mt-1'/>
      </div>
    )
  }

  function DayCard({day}) {
    const [date, time, meridiem] = day.label.split(" ")
    const score = day.score

    return (
      <div className='outline-transparent shadow-xl/30  h-140 rounded-md mx-6 mt-20 transition duration-300 ease-in-out hover:outline-1 hover:outline-white'>
        <div className='flex justify-between px-4 pt-4'>
          <h1 className='text-2xl'>{date}</h1>
          <h1 className='text-neutral-400 text-xl'>{time + ' ' + meridiem}</h1>
        </div>
        <h1 className='text-6xl font-serif text-amber-200 pt-10 text-shadow-sm/60 text-shadow-amber-100 mb-16'>{score}/6</h1>
        {day.readings.map(n => <Reading category={n.label} value={n.real} unit={n.unit} met={n.met} key={n.real}/>)}
      </div>
    )
  }

  async function handleSearch(){
    setLoading(true)
    setError(null)

    try{
      const params = new URLSearchParams({location : query})
      const res = await fetch(`http://127.0.0.1:5000/prediction?${params}`)
      if(!res.ok)throw new Error("Couldn't find that location")
      setData(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
    <div className='mt-20'>
      <h1 className='font-stretch-expanded text-4xl'>Sunsetology</h1>
      <h3 className='mt-2 font-serif'>Know the sky before you look up.</h3>
    </div>
      <ul>
      </ul>

      <div className='flex mt-20 justify-center'>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          className='inline-xl px-1 py-2 outline-none border-b border-stone-500 transition duration-300 ease-in-out focus:border-amber-200 text-3xl'
          placeholder="Irvine, CA"/>
        <button
          onClick={handleSearch}
          className='rounded-4xl ml-7 px-8 py-2 bg-amber-200 text-black hover:cursor-pointer shadow-sm shadow-amber-200/50 self-end transition duration-300 ease-in-out hover:bg-amber-300'>Check forecast</button>
      </div>

      <div className='grid grid-cols-3 justify-center'>
        {data.map(n => <DayCard day={n}></DayCard>)}
      </div>
    </>
  )
}

export default App
