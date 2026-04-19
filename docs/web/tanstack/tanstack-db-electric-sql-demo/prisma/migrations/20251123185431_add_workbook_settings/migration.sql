-- AlterTable
ALTER TABLE "workbooks" ADD COLUMN     "monthlyPayment" DECIMAL(10,2) NOT NULL DEFAULT 0,
ADD COLUMN     "strategy" VARCHAR(12) NOT NULL DEFAULT 'avalanche';
