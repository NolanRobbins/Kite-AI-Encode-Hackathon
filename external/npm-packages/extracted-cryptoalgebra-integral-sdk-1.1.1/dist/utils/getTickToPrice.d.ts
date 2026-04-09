import { Price } from '../entities';
import { AnyToken } from '../types';
export declare function getTickToPrice(baseToken?: AnyToken, quoteToken?: AnyToken, tick?: number): Price<AnyToken, AnyToken> | undefined;
