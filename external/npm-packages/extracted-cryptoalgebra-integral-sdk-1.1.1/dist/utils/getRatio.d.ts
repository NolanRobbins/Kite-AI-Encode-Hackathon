import { Currency, Price } from '../entities';
export declare function getRatio(lower: Price<Currency, Currency>, current: Price<Currency, Currency>, upper: Price<Currency, Currency>): number | undefined;
