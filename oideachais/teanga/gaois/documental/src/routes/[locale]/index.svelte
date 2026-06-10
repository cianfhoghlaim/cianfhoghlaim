<script>
	import { stores } from '@sapper/app';
	import { _, locale } from 'services/i18n';
	import settings from 'settings';
	
	import HomeResource from 'components/HomeResource.svelte';
    
    const { page } = stores();

	$: url = !!$page.params.locale ? `${settings.url}/${$locale}` : `${settings.url}`;
	$: localeAlternate = $locale === 'ga' ? 'en' : 'ga';
	$: urlAlternate = `${settings.url}/${localeAlternate}`;
	$: openGraphLocale = $locale === 'ga' ? 'ga_IE' : 'en_GB';
	$: openGraphLocaleAlternate = $locale === 'ga' ? 'en_GB' : 'ga_IE';
</script>

<svelte:head>
	<title>{$_('home.title')} | {$_('global.groupName')}</title>
	<meta property='og:title' content={$_('home.title')}>
    <meta name='twitter:title' content={`${$_('home.title')} | ${$_('global.groupName')}`}>

	<meta name='description' content={$_('global.description')}>
	<meta property='og:description' content={$_('global.description')}>
	<meta name='twitter:description' content={$_('global.description')}>
	<meta name='keywords' content={$_('global.keywords')}>

	<link rel="alternate" hreflang={localeAlternate} href={urlAlternate}>
	<meta property='og:locale' content={openGraphLocale}>
	<meta property='og:locale:alternate' content={openGraphLocaleAlternate}>
	<meta property='og:url' content={url}>
    <meta name='twitter:url' content={url}>
</svelte:head>

<div class='home'>
	<header>
		<h1>{$_('home.heading')}</h1>
		<p>{@html $_('home.tagline', { values:
			{ link: `<a href='https://www.gaois.ie/${$locale}/' rel='noopener' target='_blank'>${$_(`home.groupName`)}</a>` }
		})}</p>
	</header>
	<section>
		<h2>{$_('home.openData')}</h2>
		<ul>
			<li>
				<HomeResource 
					href={`/${$locale}/data/getting-started`}
					heading={$_('home.sections.gettingStarted')}
					blurb={$_('home.sections.gettingStartedBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/data/logainm/v1.1/api`}
					heading='Logainm'
					blurb={$_('home.sections.logainmBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/data/duchas/v0.6/api`}
					heading='Dúchas'
					blurb={$_('home.sections.duchasBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/data/surnames`}
					heading={$_('home.sections.surnames')}
					blurb={$_('home.sections.surnamesBlurb')}/>
			</li>
		</ul>
	</section>
	<section>
		<h2>{$_('home.software')}</h2>
		<ul>
			<li>
				<HomeResource 
					href={`/${$locale}/software/terminologue/intro`}
					heading='Terminologue'
					blurb={$_('home.sections.terminologueBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/software/geonames2sql`}
					heading='GeoNames2Sql'
					blurb={$_('home.sections.geoNames2SqlBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/software/localizer`}
					heading='Gaois.Localizer'
					blurb={$_('home.sections.localizerBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/software/querylogger/v0.7/intro`}
					heading='Gaois.QueryLogger'
					blurb={$_('home.sections.queryLoggerBlurb')}/>
			</li>
			<li>
				<HomeResource 
					href={`/${$locale}/software/documental/intro`}
					heading='Documental'
					blurb={$_('home.sections.documentalBlurb')}/>
			</li>
		</ul>
	</section>
	<aside>
		<p>{$_('global.tagline')}</p>
		<p>
			<a href={`https://www.gaois.ie/${$locale}/`} rel='noopener' target='_blank'>
				{$_('home.moreInfo')} »
			</a>
		</p>
	</aside>
</div>

<style>
	h2 {
		border-bottom: 1px solid #222;
		border-bottom: 1px solid var(--text-color);
		display: block;
		margin-bottom: 1rem;
		padding-bottom: 0.15rem;
		width: 100%;
	}

	ul {
		display: flex;
		flex: 1;
		flex-wrap: wrap;
		justify-content: space-between;
		margin: 0;
		padding: 0;
		list-style: none;
	}

	li {
		margin-bottom: 1rem;
		width: 100%;
	}

	header {
		margin-bottom: 3rem;
	}

	section {
		margin: 1rem 0;
	}

	aside {
		background-color: #f0f2f3;
		border-bottom: 4px solid #54c0db;
		border-bottom: 4px solid var(--primary-color);
		border-top: 4px solid #54c0db;
		border-top: 4px solid var(--primary-color);
		margin-top: 1.6rem;
		padding: 0.9rem 1rem 1rem 1rem;
	}

	aside p {
		font-size: 0.95rem;
		margin: 1rem 0;
	}

	.home {
        padding: 1rem 0;
        margin-top: 1.6rem;
        width: 100%;
	}

	@media screen and (min-width: 450px) {
		ul::after {
			content: '';
			flex: auto;
		}

		li {
			width: 48%;
			width: calc((100% - 1rem) / 2);
		}

		li:nth-last-child(1):nth-child(even) {
			margin-left: 1rem;
		}
	}

	@media screen and (min-width: 1000px) {
        .home {
            margin-top: 6rem;
			padding-left: 2rem;
		}
	}
	
	@media screen and (min-width: 1170px) {
        .home {
            max-width: 65%;
            max-width: 770px;
			padding: 1rem 2rem;
			width: 67%;
		}

		li {
			width: 32%;
			width: calc((100% - 2rem) / 3);
		}

		li:nth-last-child(1):nth-child(even) {
			margin-left: 0;
		}

		li:nth-last-child(1):nth-child(odd) {
			margin-left: 1rem;
		}

		aside {
			max-width: 400px;
			position: absolute;
			right: 1rem;
			top: 11.9rem;
			width: 22.5%;
		}
	}

    @media screen and (min-width: 1600px) {
        .home {
            margin-left: 5%;
        }
    }
</style>