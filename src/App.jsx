import { useState } from 'react'
import './App.css'


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
    <div className='outline-transparent shadow-xl/30  h-140 rounded-md transition duration-300 ease-in-out hover:outline-1 hover:outline-white'>
      <div className='flex justify-between px-4 pt-4'>
        <h1 className='text-2xl'>{date}</h1>
        <h1 className='text-neutral-400 text-xl'>{time + ' ' + meridiem}</h1>
      </div>
      <h1 className='text-6xl font-serif text-amber-200 pt-10 text-shadow-sm/60 text-shadow-amber-100 mb-16'>{score}/6</h1>
      {day.readings.map(n => <Reading category={n.label} value={n.real} unit={n.unit} met={n.met} key={n.real}/>)}
    </div>
  )
}

function App() {
  const [data, setData] = useState([])
  const [query, setQuery] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [location, setLocation] = useState("")

  async function handleSearch(){
    setLoading(true)
    setError(null)

    try{
      const params = new URLSearchParams({location : query})
      const res = await fetch(`/api/prediction?${params}`)
      const json = await res.json()
      if(!res.ok)throw new Error(json.error ?? "Couldn't reach the forecast")
      setData(json.data)
      setLocation(json.place)
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
      <h3 className='mt-2'>Pick a location...any location</h3>
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

      {loading && <div className='flex justify-center items-center mt-4'>
        <div className="animate-spin h-4 w-4 border-2 border-amber-200 border-t-transparent rounded-full mx-2"></div>
        <h1>Loading...</h1>
      </div>}
      
      {error && <div className='flex justify-center items-center mt-4'>
        <svg className="mx-2 w-6 h-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="red">
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" /></svg>
        <h1>Error! {error}</h1>
      </div>}

      {!loading && !error &&
      <div className='mx-auto max-w-7x1 px-6 mt-14'>
        <h1 className='text-left pb-2 text-3xl'>{location}</h1>
        <div className='grid grid-cols-3 gap-10 justify-center'>
          {data.map(n => <DayCard day={n}></DayCard>)}
        </div>
      </div>}
    </>
  )
}

export default App
