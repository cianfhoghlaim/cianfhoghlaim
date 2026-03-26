import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { 
  Route, 
  Database, 
  Zap, 
  Shield, 
  Palette, 
  Code,
  Server,
  Layers
} from "lucide-react"

const features = [
  {
    icon: Route,
    title: "TanStack Router",
    description: "Type-safe, file-based routing with powerful features like nested layouts, loaders, and search params validation.",
    badge: "Type-Safe"
  },
  {
    icon: Database,
    title: "TanStack Query",
    description: "Powerful data synchronization with server state management, caching, and background updates built-in.",
    badge: "Server State"
  },
  {
    icon: Code,
    title: "React 19",
    description: "Latest React with concurrent features, improved performance, and modern development patterns.",
    badge: "Latest"
  },
  {
    icon: Zap,
    title: "Vite",
    description: "Lightning-fast build tool with hot module replacement and optimized production builds.",
    badge: "Fast"
  },
  {
    icon: Shield,
    title: "TypeScript",
    description: "Full TypeScript support with strict typing, IntelliSense, and compile-time error checking.",
    badge: "Type-Safe"
  },
  {
    icon: Palette,
    title: "Tailwind CSS v4",
    description: "Modern utility-first CSS framework with CSS variables and a comprehensive design system.",
    badge: "Styling"
  },
  {
    icon: Server,
    title: "SSR Ready",
    description: "Server-side rendering support with seamless hydration and SEO optimization out of the box.",
    badge: "Performance"
  },
  {
    icon: Layers,
    title: "Shadcn/UI",
    description: "Beautiful, accessible component library with customizable themes and modern design patterns.",
    badge: "Components"
  }
]

export function FeaturesSection() {
  return (
    <section id="features" className="py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Everything you need to build modern web apps
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            A carefully curated stack of the best tools and libraries for React development
          </p>
        </div>
        
        <div className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-6 sm:mt-20 lg:mx-0 lg:max-w-none lg:grid-cols-2 xl:grid-cols-4">
          {features.map((feature) => {
            const IconComponent = feature.icon
            return (
              <Card key={feature.title} className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <IconComponent className="h-5 w-5 text-primary" />
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {feature.badge}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-sm leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </section>
  )
}