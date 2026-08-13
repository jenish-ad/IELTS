import { randomInt } from "node:crypto";
import { connection } from "next/server";

import questions from "@/data/mockquestion.json";

export default async function SpeakingPracticePage() {
  await connection();

  const prompt = questions[randomInt(questions.length)];

  return (
    <main className="flex min-h-svh justify-center">
      <section className="mt-[clamp(205px,23vh,240px)] w-[min(720px,calc(100%-36px))] text-center [text-shadow:0_4px_24px_rgb(0_0_0/38%)] max-[1000px]:mt-[195px] max-[600px]:mt-[155px]">
        <div className="rounded-[34px] border border-white/15 bg-black/35 px-10 py-9 shadow-[0_24px_55px_rgb(0_0_0/22%)] backdrop-blur-md max-[600px]:rounded-[26px] max-[600px]:px-6 max-[600px]:py-7">
          <p className="mb-4 text-[13px] font-semibold uppercase tracking-[0.2em] text-white/70">
            Speaking · Part {prompt.part}
          </p>

          <h1 className="mx-auto max-w-[610px] text-[clamp(2.4rem,4.2vw,3.8rem)] leading-[1.02] font-bold tracking-[-0.045em] text-[#fff8ed]">
            {prompt.question}
          </h1>

          <div
            className="mx-auto mt-6 h-[4px] w-[140px] -rotate-1 rounded-full bg-[#f14935]"
            aria-hidden="true"
          />
        </div>

        <button
          type="button"
          className="mx-auto mt-8 flex min-h-[68px] w-[290px] cursor-pointer items-center gap-4 rounded-full bg-gradient-to-r from-[#ff4b34] to-[#ff654f] px-7 text-[18px] shadow-[0_15px_30px_rgb(32_5_3/32%)] [text-shadow:none] transition-all duration-200 hover:-translate-y-[3px] hover:shadow-[0_20px_38px_rgb(32_5_3/40%)] max-[600px]:min-h-[62px] max-[600px]:w-[min(280px,90%)]"
        >
          <svg
            className="w-6 fill-none stroke-current stroke-[1.8] [stroke-linecap:round] [stroke-linejoin:round]"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <rect x="8" y="2" width="8" height="14" rx="4" />
            <path d="M5 11a7 7 0 0 0 14 0M12 18v4M8 22h8" />
          </svg>

          <span className="font-semibold">Start Speaking</span>

          <span className="ml-auto text-[27px] font-light" aria-hidden="true">
            →
          </span>
        </button>
      </section>
    </main>
  );
}
