import Link from "next/link"

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-10 py-4 bg-white shadow-sm">
      <div className="text-green-700 font-bold text-xl">
        IPB-NPGRL
      </div>

      <div className="space-x-8 text-green-700 font-medium">
        <Link href="#home">Home</Link>
        <Link href="#features">Features</Link>
        <Link href="#about">About</Link>
      </div>
    </nav>
  )
}