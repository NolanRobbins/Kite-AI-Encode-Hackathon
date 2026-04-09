import { BigintIsh } from '../types/BigIntish';
import { Interface } from '@ethersproject/abi';
import { AnyToken } from '../types';
export interface StandardPermitArguments {
    v: 0 | 1 | 27 | 28;
    r: string;
    s: string;
    amount: BigintIsh;
    deadline: BigintIsh;
}
export interface AllowedPermitArguments {
    v: 0 | 1 | 27 | 28;
    r: string;
    s: string;
    nonce: BigintIsh;
    expiry: BigintIsh;
}
export declare type PermitOptions = StandardPermitArguments | AllowedPermitArguments;
export declare abstract class SelfPermit {
    static INTERFACE: Interface;
    protected static encodePermit(token: AnyToken, options: PermitOptions): string;
}
