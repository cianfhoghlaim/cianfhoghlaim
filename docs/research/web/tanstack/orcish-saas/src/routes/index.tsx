import AboutUs from '@/components/shadcn-studio/blocks/about-us/about-us'
import ContactUs from '@/components/shadcn-studio/blocks/contact-us/contact-us'
import Footer from '@/components/shadcn-studio/blocks/footer-component/footer-component'
import Gallery from '@/components/shadcn-studio/blocks/gallery-component-01/gallery-component'
import HeroSection from '@/components/shadcn-studio/blocks/hero-section/hero-section'
import Navbar from '@/components/shadcn-studio/blocks/navbar-component/navbar-component'
import { createFileRoute } from '@tanstack/react-router'
import {
  Clock8Icon,
  MedalIcon,
  SparklesIcon,
  StarIcon,
  TargetIcon,
  MapPinIcon,
  PhoneIcon,
  BriefcaseBusinessIcon,
} from 'lucide-react'

export const Route = createFileRoute('/')({ component: App })

function App() {
  const gallerySections = [
    {
      images: [
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-10.png',
          alt: 'Coastal cliffs and ocean view',
        },
      ],
    },
    {
      type: 'grid',
      images: [
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-9.png',
          alt: 'Silhouettes on beach',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-8.png',
          alt: 'Snowy mountain peaks',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-7.png',
          alt: 'Rolling green hills',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-6.png',
          alt: 'Sunset landscape',
        },
      ],
    },
    {
      type: 'grid',
      images: [
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-4.png',
          alt: 'Silhouettes on beach',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-3.png',
          alt: 'Snowy mountain peaks',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-2.png',
          alt: 'Rolling green hills',
        },
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-1.png',
          alt: 'Sunset landscape',
        },
      ],
    },
    {
      images: [
        {
          src: 'https://cdn.shadcnstudio.com/ss-assets/blocks/marketing/gallery/image-5.png',
          alt: 'Coastal cliffs and ocean view',
        },
      ],
    },
  ]

  const stats = [
    {
      icon: SparklesIcon,
      value: '20+',
      description: 'Years of Experience',
    },
    {
      icon: TargetIcon,
      value: '70+',
      description: 'Successful Projects',
    },
    {
      icon: StarIcon,
      value: '550+',
      description: 'Customer Reviews',
    },
    {
      icon: MedalIcon,
      value: '25',
      description: 'Achieve Awards',
    },
  ]

  const contactInfo = [
    {
      title: 'Office Hours',
      icon: Clock8Icon,
      description: 'Monday-Friday\n8:00 am to 5:00 pm',
    },
    {
      title: 'Our Address',
      icon: MapPinIcon,
      description: '802 Perston Rd,Maine\n96812, USA',
    },
    {
      title: 'Office 2',
      icon: BriefcaseBusinessIcon,
      description: '802 Perston Rd,Maine\n96812, USA',
    },
    {
      title: 'Get in Touch',
      icon: PhoneIcon,
      description: '+1-316-888-9685\n+1-316-477-0169',
    },
  ]

  return (
    <>
      <Navbar navigationData={[]} />
      <HeroSection />
      <Gallery sections={gallerySections} />
      <AboutUs stats={stats} />
      <ContactUs contactInfo={contactInfo} />
      <Footer />
    </>
  )
}
