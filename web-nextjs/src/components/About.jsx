import { Separator } from "@/components/ui/separator";

const GREEN = "#2d6a2d";
const GOLD = "#d4af37";
const GREEN_LIGHT = "#4a9e4a";

export default function About() {
  return (
    <section id="about" className="bg-white border-t border-b border-gray-200 py-20">
        <div className="max-w-4xl mx-auto px-6">
          <h2 className="text-3xl font-extrabold text-center mb-2" style={{ color: GREEN }}>
            About NPGRL
          </h2>
          <Separator className="mx-auto w-16 mb-10" style={{ background: GOLD, height: 3 }} />

          <div className="space-y-6 text-sm text-gray-700 leading-relaxed">
            <div>
              <h3 className="font-bold mb-1" style={{ color: GREEN_LIGHT }}>
                Establishment
              </h3>
              <p>
                The NPGRL was established on November 12, 1976 by Presidential Decree 1046-A as one
                of the component units of the Institute of Plant Breeding (IPB) and the National
                Center for Plant Genetic Resources activities. Its aim are to provide IPB and the
                national crop improvement programs a broad range of genetic materials for breeding
                superior crop varieties, and to help minimize the rapid erosion of natural
                variability existing in our cultivated species and wild relatives.
              </p>
            </div>

            <div>
              <h3 className="font-bold mb-1" style={{ color: GREEN_LIGHT }}>
                General Objectives
              </h3>
              <p>
                To acquire, characterize, evaluate, regenerate, distribute, converse, and document
                germplasm of important and potentially useful agricultural crops.
              </p>
            </div>

            <div>
              <h3 className="font-bold mb-1" style={{ color: GREEN_LIGHT }}>
                Functions
              </h3>
              <ul className="list-disc list-inside space-y-2 ml-1">
                <li>Conserves for national posterity the endemic and introduced plant genetic resources;</li>
                <li>
                  Provide plant breeding projects in the national research system with a broad
                  genetic base for crop improvement;
                </li>
                <li>
                  Monitors and coordinates national efforts in the collection, conservation,
                  utilization, and exchange of plant genetic resources.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>
  )
}