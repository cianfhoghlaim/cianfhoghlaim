// === ARCHIVED 2026-06-24 ===
// The 6 functions in this file (ExtractProfileFromCV,
// ExtractProfileFromGitHubReadme, ExtractMusicProfile,
// ExtractGameProject, MergeProfiles, GenerateProfileSummary)
// have no current Python consumer in the oideachais quadrant.
// They are intended for the croilar/ portfolio surface (per
// `croilar/AGENTS.md`), which is not yet built for persona
// profiles beyond the existing static pages.
//
// To re-activate:
// 1. Implement the consumer (e.g.
//    croilar/dagster_assets/profile_extraction.py OR
//    meaisinfhoghlaim/agents/croilar_cv_extraction.py)
// 2. Move this file back to baml_src/ (git mv)
// 3. Remove the ARCHIVED header from the top
// 4. Update STATUS.md to mark the functions as wired
// 5. Update REFACTORING.md to remove the archive entry
//
// Reference: openspec/changes/archive-celtic-baml-orphans/
// =====================================================================

// =============================================================================
// PORTFOLIO EXTRACTION SCHEMA
// =============================================================================
// BAML schemas for extracting profile data from various sources:
// - CV/Resume documents
// - GitHub profiles and READMEs
// - Spotify/SoundCloud artist data
// - LinkedIn profiles
// - Personal websites
//
// Used by multi-tenant portfolio system for cianfhoghlaim.ie and aleyum.com
// =============================================================================

// =============================================================================
// ENUMS
// =============================================================================

enum ProfileType {
    DEVELOPER @description("Software developer/engineer profile")
    MUSICIAN @description("Music producer/artist profile")
    EDUCATOR @description("Educator/teacher profile")
    RESEARCHER @description("Academic/researcher profile")
    HYBRID @description("Multi-disciplinary profile")
}

enum SkillCategory {
    PROGRAMMING_LANGUAGE @description("Programming languages like Python, TypeScript, Rust")
    FRAMEWORK @description("Frameworks like React, FastAPI, TanStack")
    DATABASE @description("Database technologies like PostgreSQL, DuckDB")
    DEVOPS @description("DevOps tools like Docker, Kubernetes, CI/CD")
    CLOUD @description("Cloud platforms like AWS, GCP, Cloudflare")
    AI_ML @description("AI/ML technologies like PyTorch, LangChain")
    GAME_ENGINE @description("Game engines like Unity, Unreal, Godot")
    AUDIO @description("Audio production tools like Ableton, Logic Pro")
    DESIGN @description("Design tools like Figma, Adobe Suite")
    LANGUAGE @description("Natural languages (human languages)")
    OTHER @description("Other skills not fitting above categories")
}

enum ProjectStatus {
    ACTIVE @description("Currently being developed")
    COMPLETED @description("Finished project")
    ARCHIVED @description("No longer maintained")
    CONCEPT @description("Planning/concept stage")
}

enum MusicGenre {
    ELECTRONIC @description("Electronic music including EDM, house, techno")
    AMBIENT @description("Ambient and atmospheric music")
    EXPERIMENTAL @description("Experimental and avant-garde")
    INDIE @description("Indie music")
    SOUNDTRACK @description("Film/game soundtracks")
    CELTIC @description("Celtic traditional or Celtic fusion")
    OTHER @description("Other genres")
}

enum PlatformType {
    GITHUB @description("GitHub repository or profile")
    SPOTIFY @description("Spotify artist or playlist")
    SOUNDCLOUD @description("SoundCloud profile or tracks")
    YOUTUBE @description("YouTube channel or videos")
    LINKEDIN @description("LinkedIn profile")
    PERSONAL_WEBSITE @description("Personal portfolio website")
    TWITTER @description("Twitter/X profile")
    OTHER @description("Other platforms")
}

// =============================================================================
// CORE TYPES
// =============================================================================

// Contact information
class ContactInfo {
    email string? @description("Primary email address")
    phone string? @description("Phone number")
    location string? @description("City, Country or general location")
    website string? @description("Personal website URL")
    linkedin string? @description("LinkedIn profile URL or username")
    github string? @description("GitHub username or profile URL")
    twitter string? @description("Twitter/X handle")
}

// Technical skill with proficiency level
class Skill {
    name string @description("Skill name, e.g., 'Python', 'React', 'Docker'")
    category SkillCategory @description("Category of the skill")
    proficiency int? @description("Proficiency level 1-5 (1=beginner, 5=expert)")
    yearsExperience int? @description("Years of experience with this skill")
    keywords string[] @description("Related keywords or sub-skills")
}

// Work experience entry
class Experience {
    company string @description("Company or organization name")
    title string @description("Job title or role")
    location string? @description("Location of the role")
    startDate string? @description("Start date (YYYY-MM format)")
    endDate string? @description("End date (YYYY-MM format, null if current)")
    isCurrent bool @description("Whether this is the current role")
    description string @description("Description of responsibilities and achievements")
    highlights string[] @description("Key achievements or highlights")
    technologies string[] @description("Technologies used in this role")
}

// Education entry
class Education {
    institution string @description("University, college, or school name")
    degree string @description("Degree type (e.g., BSc, MSc, PhD)")
    field string @description("Field of study")
    location string? @description("Location of institution")
    startDate string? @description("Start date (YYYY format)")
    endDate string? @description("End date (YYYY format)")
    grade string? @description("Grade/GPA/classification if available")
    description string? @description("Additional details about the education")
}

// Project entry
class Project {
    name string @description("Project name")
    description string @description("Project description")
    status ProjectStatus @description("Current status of the project")
    url string? @description("URL to project (repo, demo, etc.)")
    technologies string[] @description("Technologies used")
    highlights string[] @description("Key features or achievements")
    startDate string? @description("When the project started")
    endDate string? @description("When the project ended (null if ongoing)")
    role string? @description("Your role in the project")
    category string? @description("Category like 'web', 'game', 'ai', 'data'")
}

// Social/platform link
class SocialLink {
    platform PlatformType @description("Platform type")
    url string @description("Full URL to the profile")
    username string? @description("Username on the platform")
    followers int? @description("Number of followers if available")
}

// =============================================================================
// MUSIC-SPECIFIC TYPES (for aleyum.com)
// =============================================================================

// Music track or release
class MusicTrack {
    title string @description("Track title")
    artist string @description("Artist name (could be alias)")
    album string? @description("Album name if part of an album")
    releaseDate string? @description("Release date (YYYY-MM-DD)")
    duration int? @description("Duration in seconds")
    genres MusicGenre[] @description("Genres of the track")
    streamingUrls map<string, string> @description("Map of platform to URL")
    playCount int? @description("Total play count across platforms")
    isOriginal bool @description("Whether this is an original composition")
}

// Music album or EP
class MusicRelease {
    title string @description("Album/EP title")
    artist string @description("Artist name")
    releaseDate string? @description("Release date")
    tracks MusicTrack[] @description("Tracks in the release")
    artwork string? @description("Cover artwork URL")
    label string? @description("Record label if any")
    type string @description("Album, EP, Single, etc.")
}

// Music profile data from streaming platforms
class MusicProfile {
    artistName string @description("Main artist/producer name")
    aliases string[] @description("Other names/aliases used")
    bio string? @description("Artist biography")
    genres MusicGenre[] @description("Primary genres")
    monthlyListeners int? @description("Monthly listeners (Spotify)")
    followers int? @description("Total followers across platforms")
    releases MusicRelease[] @description("Discography")
    topTracks MusicTrack[] @description("Top/popular tracks")
    collaborators string[] @description("Frequent collaborators")
    equipment string[] @description("Production equipment/software")
    influences string[] @description("Musical influences")
}

// =============================================================================
// GAME DEV SPECIFIC TYPES (for aleyum.com game showcase)
// =============================================================================

// Game engine/technology
class GameTechnology {
    name string @description("Technology name like 'Unity', 'Unreal', 'Godot'")
    category string @description("Category like 'engine', 'shader', 'networking'")
    proficiency int? @description("Proficiency level 1-5")
    projects string[] @description("Projects using this technology")
}

// Game project
class GameProject {
    title string @description("Game/project title")
    description string @description("Project description")
    engine string @description("Game engine used")
    platforms string[] @description("Target platforms")
    technologies string[] @description("Other technologies used")
    role string @description("Your role (e.g., 'Lead Developer', 'Sound Designer')")
    status ProjectStatus @description("Project status")
    demoUrl string? @description("Playable demo URL")
    repoUrl string? @description("Source code repository")
    mediaUrls string[] @description("Screenshots, videos, etc.")
    releaseDate string? @description("Release date if published")
}

// =============================================================================
// COMPLETE PROFILE TYPES
// =============================================================================

// Developer-focused profile
class DeveloperProfile {
    name string @description("Full name")
    title string @description("Professional title")
    summary string @description("Professional summary/bio")
    contact ContactInfo @description("Contact information")
    skills Skill[] @description("Technical skills")
    experience Experience[] @description("Work experience")
    education Education[] @description("Education history")
    projects Project[] @description("Notable projects")
    certifications string[] @description("Professional certifications")
    publications string[] @description("Papers, articles, blog posts")
    socialLinks SocialLink[] @description("Social media/platform links")
    languages string[] @description("Natural languages spoken")
}

// Music producer profile
class MusicProducerProfile {
    name string @description("Real name")
    stageName string @description("Stage/artist name")
    title string @description("e.g., 'Music Producer & Sound Designer'")
    bio string @description("Artist biography")
    contact ContactInfo @description("Contact information")
    musicProfile MusicProfile @description("Music-specific data")
    technicalSkills Skill[] @description("Audio/technical skills")
    gameAudio GameProject[] @description("Game audio projects if any")
    socialLinks SocialLink[] @description("Platform links")
}

// Combined/hybrid profile (for aleyum.com type portfolios)
class HybridProfile {
    name string @description("Full name")
    primaryName string @description("Name to display (could be stage name)")
    title string @description("Combined professional title")
    summary string @description("Overall professional summary")
    contact ContactInfo @description("Contact information")
    profileType ProfileType @description("Primary profile type")

    // Developer aspects
    technicalSkills Skill[] @description("Technical/programming skills")
    projects Project[] @description("Software projects")
    experience Experience[] @description("Work experience")
    education Education[] @description("Education")

    // Creative aspects
    musicProfile MusicProfile? @description("Music profile if applicable")
    gameProjects GameProject[] @description("Game development projects")
    creativeWorks Project[] @description("Other creative works")

    socialLinks SocialLink[] @description("All social/platform links")
    languages string[] @description("Languages spoken")
}

// =============================================================================
// EXTRACTION FUNCTIONS
// =============================================================================

// Extract profile from CV/resume document
function ExtractProfileFromCV(document: string) -> HybridProfile {
    client Extractor
    prompt #"
        Extract a complete professional profile from the following CV/resume document.

        Analyze the document and extract:
        1. Personal information (name, contact details)
        2. Professional summary or objective
        3. Work experience with dates and achievements
        4. Education history
        5. Technical and soft skills with categories
        6. Projects and portfolio items
        7. Certifications and awards
        8. Languages spoken
        9. Social media links if mentioned

        For skills, categorize them appropriately:
        - PROGRAMMING_LANGUAGE for code languages
        - FRAMEWORK for libraries/frameworks
        - DATABASE for data storage technologies
        - DEVOPS for deployment/infrastructure tools
        - CLOUD for cloud platforms
        - AI_ML for machine learning tools
        - GAME_ENGINE for game development engines
        - AUDIO for music/audio production
        - DESIGN for visual design tools
        - LANGUAGE for human languages

        Determine if this is primarily a DEVELOPER, MUSICIAN, EDUCATOR, RESEARCHER, or HYBRID profile.

        CV/Resume Document:
        {{ document }}
    "#
}

// Extract profile from GitHub README
function ExtractProfileFromGitHubReadme(readme: string, username: string) -> DeveloperProfile {
    client Extractor
    prompt #"
        Extract a developer profile from a GitHub README profile.

        GitHub Username: {{ username }}

        README Content:
        {{ readme }}

        Extract:
        1. Name and professional title
        2. Bio/summary from the README
        3. Skills mentioned or shown via badges/icons
        4. Projects highlighted in the README
        5. Social links mentioned
        6. Any statistics or achievements mentioned
        7. Contact information if available

        For skills shown as badges (e.g., shields.io badges), identify the technology name.
    "#
}

// Extract music profile from Spotify/SoundCloud data
function ExtractMusicProfile(platformData: string, platform: PlatformType) -> MusicProfile {
    client Extractor
    prompt #"
        Extract a music producer profile from streaming platform data.

        Platform: {{ platform }}

        Platform Data:
        {{ platformData }}

        Extract:
        1. Artist name and any aliases
        2. Biography text
        3. Primary genres
        4. Listener/follower statistics
        5. Discography (albums, EPs, singles)
        6. Popular/top tracks with stream counts
        7. Collaborators if mentioned
        8. Any equipment/software mentioned
        9. Musical influences mentioned
    "#
}

// Extract game project details from documentation/README
function ExtractGameProject(projectDocs: string) -> GameProject {
    client Extractor
    prompt #"
        Extract game project information from the following documentation.

        Documentation:
        {{ projectDocs }}

        Extract:
        1. Project title and description
        2. Game engine used (Unity, Unreal, Godot, etc.)
        3. Target platforms
        4. Technologies and tools used
        5. Development status
        6. Demo URL if available
        7. Repository URL if available
        8. Media URLs (screenshots, trailers)
        9. Your role in the project
    "#
}

// Merge profiles from multiple sources into unified profile
function MergeProfiles(profiles: HybridProfile[]) -> HybridProfile {
    client Extractor
    prompt #"
        Merge the following profile extractions into a single unified profile.

        Profiles from different sources:
        {{ profiles }}

        Rules for merging:
        1. Use the most complete/detailed version of each field
        2. Combine skills, removing duplicates
        3. Combine projects, removing duplicates
        4. Combine experience entries, removing duplicates
        5. Keep all unique social links
        6. Use the most recent contact information
        7. Merge summaries into a cohesive bio
        8. Determine the overall profile type based on content weight
    "#
}

// Generate profile summary for a specific tenant context
function GenerateProfileSummary(
    profile: HybridProfile,
    tenantType: ProfileType,
    maxLength: int
) -> string {
    client ExtractorFast
    prompt #"
        Generate a professional summary for the following profile.

        Profile:
        {{ profile }}

        Target Context: {{ tenantType }}
        Maximum Length: {{ maxLength }} characters

        {% if tenantType == ProfileType.MUSICIAN %}
        Focus on: Music production experience, genres, releases, collaborations
        {% elif tenantType == ProfileType.DEVELOPER %}
        Focus on: Technical skills, projects, experience, technologies
        {% elif tenantType == ProfileType.EDUCATOR %}
        Focus on: Teaching experience, curriculum development, educational projects
        {% else %}
        Create a balanced summary covering all aspects
        {% endif %}

        Write a compelling, third-person professional summary.
    "#
}

// =============================================================================
// TESTS
// =============================================================================

test ExtractProfileFromCVTest {
    functions [ExtractProfileFromCV]
    args {
        document #"
            CONOR HYNES
            Music Producer & Game Developer
            Dublin, Ireland
            conor@aleyum.com | github.com/aleyum | spotify.com/artist/aleyum

            SUMMARY
            Electronic music producer and game developer with 5+ years experience
            creating ambient soundscapes and interactive audio experiences.

            SKILLS
            - Audio: Ableton Live, Logic Pro X, Max/MSP
            - Game Dev: Unity, Unreal Engine 5, FMOD
            - Programming: C#, Python, TypeScript

            EXPERIENCE
            Freelance Music Producer | 2019 - Present
            - Released 3 EPs on indie labels
            - Composed soundtracks for 5 indie games

            EDUCATION
            BA Music Technology | Trinity College Dublin | 2019
        "#
    }
}

test ExtractMusicProfileTest {
    functions [ExtractMusicProfile]
    args {
        platformData #"
            Artist: Aleyum
            Monthly Listeners: 15,432
            Genres: Electronic, Ambient, Experimental

            Top Tracks:
            1. Connemara Dreams - 45,000 plays
            2. Celtic Circuits - 32,000 plays
            3. Digital Fog - 28,000 plays

            Albums:
            - "Spectral Waves" EP (2024) - 6 tracks
            - "Memory Palace" (2023) - 10 tracks
        "#
        platform PlatformType.SPOTIFY
    }
}
