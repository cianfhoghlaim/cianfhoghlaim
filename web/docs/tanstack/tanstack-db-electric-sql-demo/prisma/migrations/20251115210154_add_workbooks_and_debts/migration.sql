-- CreateTable
CREATE TABLE "debts" (
    "id" UUID NOT NULL,
    "workbookId" UUID NOT NULL,
    "name" VARCHAR(48) NOT NULL,
    "type" VARCHAR(12) NOT NULL,
    "rate" DECIMAL(5,3) NOT NULL,
    "balance" DECIMAL(10,2) NOT NULL,
    "minPayment" DECIMAL(10,2) NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "debts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "workbooks" (
    "id" UUID NOT NULL,
    "name" VARCHAR(48) NOT NULL,
    "ownerId" UUID NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "workbooks_pkey" PRIMARY KEY ("id")
);

-- AddCheckConstraints
ALTER TABLE "debts" ADD CONSTRAINT "debts_type_check" CHECK ("type" IN ('auto', 'home', 'credit', 'school', 'personal', 'other'));
ALTER TABLE "debts" ADD CONSTRAINT "debts_rate_check" CHECK ("rate" >= 0);
ALTER TABLE "debts" ADD CONSTRAINT "debts_balance_check" CHECK ("balance" >= 0);
ALTER TABLE "debts" ADD CONSTRAINT "debts_minPayment_check" CHECK ("minPayment" >= 0);

-- CreateIndex
CREATE INDEX "debts_workbookId_name_idx" ON "debts"("workbookId", "name");

-- CreateIndex
CREATE INDEX "workbooks_ownerId_name_idx" ON "workbooks"("ownerId", "name");

-- CreateIndex
CREATE INDEX "verifications_identifier_expiresAt_idx" ON "verifications"("identifier", "expiresAt" DESC);

-- AddForeignKey
ALTER TABLE "debts" ADD CONSTRAINT "debts_workbookId_fkey" FOREIGN KEY ("workbookId") REFERENCES "workbooks"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "workbooks" ADD CONSTRAINT "workbooks_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
