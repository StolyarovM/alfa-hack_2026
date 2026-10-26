
export const isInnValid = (inn: string) => /^\d{10}$|^\d{12}$/.test(inn);
export const isPositiveMoney = (n: number) => Number.isFinite(n) && n > 0;
