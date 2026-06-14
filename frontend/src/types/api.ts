export type Row = Record<string, string | number | boolean | null>;
export interface Envelope<T> { data: T; license: string; sources: string[] }
export interface Page<T> extends Envelope<T[]> { total: number; page: number; page_size: number }
