import { request } from "./api";

function App() {

  const handleClick = async () => {
    let x  = await request();
    console.log(x)
  }


  return (
    <>
    <h1>EasyDen Smart Home System</h1>
    <button onClick={handleClick}>Request</button>
  </>
  );
}

export default App;
