import Link from 'next/link';

export function Footnote() {
  return (
    <div className="text-xs text-zinc-400 leading-5 hidden sm:block">
      This preview is built using{' '}
      <Link
        className="underline underline-offset-2"
        href="https://thirdweb.com/x402"
        target="_blank"
      >
        thirdweb x402 stack
      </Link>
      . Read more about how to use integrate this into your application in our{' '}
      <Link
        className="underline underline-offset-2"
        href="https://portal.thirdweb.com/x402"
        target="_blank"
      >
        documentation
      </Link>
      .
    </div>
  );
}
