import { Inter } from 'next/font/google'
import * as React from "react";
import axios, { isAxiosError } from "axios";
import Image from 'next/image'

const inter = Inter({ subsets: ['latin'] })

const API_ENDPOINT = "https://rachelspark--img-fusion-fastapi-app.modal.run/generate-image";

export default function Home() {
  const [file1, setFile1] = React.useState<File>();
  const [file2, setFile2] = React.useState<File>();
  const [generatedImage, setGeneratedImage] = React.useState(null);
  const [loading, setLoading] = React.useState(false)
  const [errorMessage, setErrorMessage] = React.useState("");

  const generateImage = async () => {
    if (!file1 || !file2) {
      setErrorMessage("Please upload two images");
      return;
    }
    try {
      setLoading(true)
      setErrorMessage("")
      const formData = new FormData();
      const headers = {
        accept: "application/json",
        "Content-Type": "multipart/form-data",
      };
      formData.append("file1", file1!);
      formData.append("file2", file2!);
      const axiosResponse = await axios.post(API_ENDPOINT, formData, {
        headers: headers
      })
      setGeneratedImage(axiosResponse.data![0]['image'])

      // resetting error and loading states
      setLoading(false)
      setErrorMessage("")
    } catch (e: unknown) {
      setLoading(false)
      if (isAxiosError(e)) {
        setErrorMessage("Sorry, we're running into an issue. Please try again in a bit!")
      }
    }
  }

  return (
    <main
      className={`flex min-h-screen flex-col items-center justify-between p-24 ${inter.className}`}
    >
      <div>
        <div className="relative text-center pb-10">
          <div className="animate-text bg-gradient-to-r from-purple-200 via-violet-400 to-indigo-400 bg-clip-text text-transparent text-7xl px-2 pb-6 font-black">
            Image Fusion
          </div>
          <div className="text-xl text-slate-200">Blend images together using Kandinsky 2</div>
        </div>
        <div className="bg-slate-900 rounded-md py-10 grid justify-items-center">
          <div className="">
          <form>
            <fieldset className="pb-4">
              <input onChange={(e) => {setFile1(e.target.files![0]);}} name="image1" type="file" accept='.jpeg, .png, .jpg'></input>
            </fieldset>
            <fieldset>
            <input onChange={(e) => {setFile2(e.target.files![0]);}} name="image1" type="file" accept='.jpeg, .png, .jpg'></input>
            </fieldset>
          </form>
          </div>
          {!loading ? 
            <button onClick={generateImage} className="rounded px-6 py-3 mt-12 text-lg bg-gradient-to-l from-purple-800 via-violet-800 to-indigo-800">Generate</button> 
            : <button className="rounded px-4 py-3 mt-12 text-lg flex flex-row bg-gradient-to-l from-purple-800 via-violet-800 to-indigo-800" disabled>
              Generating
              <svg className="animate-spin ml-2 mt-1 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-50" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              </button>}
          {errorMessage && (
            <div className="text-red-500 text-center text-wrap text-md pt-4 mx-4">
              {errorMessage}
            </div>
          )}
        {generatedImage && (
          <div className="m-2 pt-10">
            <Image src={`data:image/png;base64,${generatedImage}`} alt={''} width={500} height={500}/>
          </div>
        )}
        </div>
      </div>
    </main>
  )
}

