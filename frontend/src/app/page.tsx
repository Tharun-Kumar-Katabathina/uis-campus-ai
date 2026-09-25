export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex w-full max-w-2xl flex-col items-center gap-4 px-6 py-32 text-center">
        <h1 className="text-3xl font-semibold tracking-tight text-black dark:text-zinc-50">
          UIS CampusAI
        </h1>
        <p className="max-w-md text-lg leading-7 text-zinc-600 dark:text-zinc-400">
          Ask a question about UIS academics, the calendar, the library, campus
          events, or student organizations.
        </p>
      </main>
    </div>
  );
}
