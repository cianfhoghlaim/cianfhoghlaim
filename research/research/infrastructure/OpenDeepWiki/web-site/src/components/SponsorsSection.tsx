// 赞助商展示组件

import { useTranslation } from 'react-i18next'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { sponsors } from '@/data/sponsors'
import type { Sponsor } from '@/data/sponsors'

interface SponsorsSectionProps {
  title?: string
  className?: string
}

export const SponsorsSection: React.FC<SponsorsSectionProps> = ({
  title,
  className = ''
}) => {
  const { t } = useTranslation()
  const displayTitle = title || t('home.sponsors.title')
  
  const handleSponsorClick = (sponsor: Sponsor) => {
    window.open(sponsor.url, '_blank', 'noopener,noreferrer')
  }

  return (
    <section className={`py-16 ${className}`}>
      <div className="container mx-auto px-4">
        <h3 className="text-3xl font-bold text-center mb-12 text-foreground">
          {displayTitle}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-4xl mx-auto">
          {sponsors.map((sponsor, index) => (
            <Card 
              key={index} 
              className="group cursor-pointer hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
              onClick={() => handleSponsorClick(sponsor)}
            >
              <CardContent className="p-6 text-center">
                <div className="flex flex-col items-center space-y-4">
                  <Avatar className="h-16 w-16 group-hover:scale-110 transition-transform duration-300">
                    <AvatarImage 
                      src={sponsor.logo} 
                      alt={sponsor.name}
                      className="object-contain"
                    />
                    <AvatarFallback className="bg-muted text-muted-foreground text-lg font-semibold">
                      {sponsor.name.slice(0, 2)}
                    </AvatarFallback>
                  </Avatar>
                  
                  <div className="space-y-2">
                    <h4 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                      {sponsor.name}
                    </h4>
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {sponsor.description}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="text-center mt-12">
          <p className="text-sm text-muted-foreground">
            {t('home.sponsors.thanks')}
          </p>
        </div>
      </div>
    </section>
  )
}

export default SponsorsSection