import type { ReactElement } from 'react';
export function SourceMetadata({ license, sources }: {license: string; sources: string[]}): ReactElement {
  return <footer>Source: {sources.join(', ')} · {license}</footer>;
}
