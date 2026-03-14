import { MenuIcon, SearchIcon } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

import Logo from '@/components/shadcn-studio/logo'
import { ModeToggle } from '@/components/mode-toggle'
import { Link } from '@tanstack/react-router'

type NavigationItem = {
  title: string
  href: string
}[]

const Navbar = ({ navigationData }: { navigationData: NavigationItem }) => {
  return (
    <header className="bg-background sticky top-0 z-50">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-8 px-4 py-7 sm:px-6">
        <div className="text-muted-foreground flex flex-1 items-center gap-8 font-medium md:justify-center lg:gap-16">
          <a href="#home" className="hover:text-primary max-md:hidden">
            Home
          </a>
          <a href="#products" className="hover:text-primary max-md:hidden">
            Products
          </a>
          <a href="#home" className="hover:text-primary max-md:hidden">
            <Logo className="text-foreground gap-3" />
          </a>
          <a href="#about-us" className="hover:text-primary max-md:hidden">
            About Us
          </a>
          <a href="#contacts" className="hover:text-primary max-md:hidden">
            Contacts
          </a>
        </div>

        <div className="flex items-center gap-6">
          <Button variant="outline" asChild>
            <Link to="/dashboard">Dashboard</Link>
          </Button>
          <ModeToggle />
          <DropdownMenu>
            <DropdownMenuTrigger className="md:hidden" asChild>
              <Button variant="outline" size="icon">
                <MenuIcon />
                <span className="sr-only">Menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end">
              <DropdownMenuGroup>
                {navigationData.map((item, index) => (
                  <DropdownMenuItem key={index}>
                    <a href={item.href}>{item.title}</a>
                  </DropdownMenuItem>
                ))}
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  )
}

export default Navbar
