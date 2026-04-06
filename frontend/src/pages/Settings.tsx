export default function Settings() {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Settings</h1>
      <div className="bg-gray-900 rounded-lg p-6 border border-gray-800">
        <p className="text-gray-400 text-sm">Configure API keys and collection schedules in <code className="text-gray-300">.env</code> file. Restart the backend to apply changes.</p>
        <div className="mt-4 space-y-3 text-sm">
          <div><span className="text-gray-400">Backend: </span><code className="text-gray-300">uvicorn backend.main:app --reload</code></div>
          <div><span className="text-gray-400">Frontend: </span><code className="text-gray-300">cd frontend && npm run dev</code></div>
        </div>
      </div>
    </div>
  )
}
