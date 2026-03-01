import { BookOpen, Send, FlaskConical, ShieldCheck, FolderOpen, FileText } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import Image from "next/image"

const GREEN = "#2d6a2d";
const GOLD = "#e8b84b";
const GREEN_LIGHT = "#4a9e4a";
const features = [
  {
    icon: BookOpen,
    title: "Germplasm Catalog",
    desc: "Browse and search accessions of conserved plant genetic resources with details on origin, characteristics, and availability.",
    image: "/gc.jpg"
  },
  {
    icon: Send,
    title: "Request & Distribution",
    desc: "Submit germplasm request for research or breeding programs and track status through the platform.",
    image: "/gc.jpg"
  },
  {
    icon: FlaskConical,
    title: "Characterization & Evaluation Data",
    desc: "View detailed characterization and evaluation results of plant accessions to support informed selection.",
    image: "/gc.jpg"
  },
  {
    icon: ShieldCheck,
    title: "Conservation Status",
    desc: "Track conservation activities such as regeneration, viability testing, and storage condition of accessions.",
    image: "/gc.jpg"
  },
  {
    icon: FolderOpen,
    title: "Collection Management",
    desc: "Tools for managing field and seed bank collections, including location tracking, lot inventory, and history.",
    image: "/gc.jpg"
  },
  {
    icon: FileText,
    title: "Documentation & Reports",
    desc: "Access projects documents, national reports, and coordinated efforts on genetic resource management.",
    image: "/gc.jpg"
  },
];

export default function Features() {
  return (
    <section id="features" className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-extrabold mb-2" style={{ color: GREEN }}>
            Core Features
          </h2>
          <Separator className="mx-auto w-16 mt-3" style={{ background: GOLD, height: 3 }} />
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc, image }) => (
            <Card
              key={title}
              className="group overflow-hidden border border-gray-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
            >
              {/* mini passport preview at top photo*/}
              <div className="relative w-full h-40">
                <Image
                src={image}
                alt={title}
                fill
                className="object-cover"
                />
            </div>

              <CardHeader className="pb-2 pt-4">
                <div className="flex items-center gap-2">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ background: GREEN + "15" }}
                  >
                    <Icon className="w-4 h-4" style={{ color: GREEN }} />
                  </div>
                  <CardTitle
                    className="text-sm font-bold leading-tight"
                    style={{ color: GREEN_LIGHT }}
                  >
                    {title}
                  </CardTitle>
                </div>
              </CardHeader>

              <CardContent>
                <CardDescription className="text-gray-600 text-xs leading-relaxed">
                  {desc}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
  );
}