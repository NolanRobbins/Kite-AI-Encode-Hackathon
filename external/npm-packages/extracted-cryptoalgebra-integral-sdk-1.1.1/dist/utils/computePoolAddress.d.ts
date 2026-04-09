import { Token } from '../entities';
import { AnyToken } from '../types';
/**
 * Computes a pool address
 * @param poolDeployer The Algebra Pool Deployer address
 * @param tokenA The first token of the pair, irrespective of sort order
 * @param tokenB The second token of the pair, irrespective of sort order
 * @param initCodeHashManualOverride The initial code hash override
 * @returns The pool address
 */
export declare function computePoolAddress({ tokenA, tokenB, initCodeHashManualOverride, poolDeployer, }: {
    tokenA: AnyToken;
    tokenB: AnyToken;
    initCodeHashManualOverride?: string;
    poolDeployer?: string;
}): string;
export declare function computeCustomPoolAddress({ tokenA, tokenB, customPoolDeployer, initCodeHashManualOverride, mainPoolDeployer, }: {
    tokenA: AnyToken;
    tokenB: AnyToken;
    customPoolDeployer: string;
    initCodeHashManualOverride?: string;
    mainPoolDeployer?: string;
}): string;
export declare function computePoolAddressZkSync({ poolDeployer, tokenA, tokenB, initCodeHashManualOverride, }: {
    tokenA: Token;
    tokenB: Token;
    initCodeHashManualOverride?: string;
    poolDeployer?: string;
}): string;
