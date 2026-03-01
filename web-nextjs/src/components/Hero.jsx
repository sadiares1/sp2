import Image from "next/image";
import { Button } from "@/components/ui/button";
import LoginModal from "@/components/modals/AuthModals";

const GREEN = "#2d6a2d";
const GOLD = "#e8b84b";

export default function Hero() {
  return (
    <section
        id="home"
        className="relative overflow-hidden"
        style={{ background: GREEN }}
      >
        <div className="max-w-6xl mx-auto relative">
          <div className="grid md:grid-cols-2 items-stretch min-h-[280px]">

            {/* LEFT — text content */}
            <div className="flex flex-col justify-center px-8 py-16 md:py-20 z-10 relative">
              <h1 className="text-3xl md:text-4xl font-extrabold text-white leading-tight mb-3">
                Welcome to PHLGRIS
              </h1>
              <p className="text-green-100 text-sm md:text-base mb-8 max-w-md">
                Philippine Plant Genetic Resources Information and Data Management System
              </p>
              <div>
                <LoginModal/>
              </div>
            </div>

            <div className="relative w-full h-full min-h-[300px] md:min-h-0">
              <Image
                src="/hero.jpg"
                alt="Field Research"
                fill
                className="object-cover object-center"
                priority
              />
            </div>
          </div>
        </div>

        {/* Bottom wave */}
        <div className="relative z-10 -mb-1">
          <svg
            viewBox="0 0 1440 80"
            className="w-full block"
            preserveAspectRatio="none"
            style={{ height: 60 }}
          >
            <path
              d="M0,40 C360,90 1080,-10 1440,40 L1440,80 L0,80 Z"
              fill="#f7f9f4"
            />
          </svg>
        </div>
      </section>
  );
}