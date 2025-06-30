import { newsletters, admins, type Newsletter, type InsertNewsletter, type Admin } from "@shared/schema";
import { db } from "./db";
import { eq } from "drizzle-orm";
import bcrypt from "bcryptjs";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  createNewsletter(newsletter: InsertNewsletter): Promise<Newsletter>;
  getNewsletters(): Promise<Newsletter[]>;
  deleteNewsletter(id: number): Promise<void>;
  getAdminByUsername(username: string): Promise<Admin | undefined>;
  verifyAdmin(username: string, password: string): Promise<boolean>;
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    //Implementation for fetching user from database based on ID.  Implementation needed.
    throw new Error("Method not implemented.");
  }
  async getUserByUsername(username: string): Promise<User | undefined> {
    //Implementation for fetching user from database based on username. Implementation needed.
    throw new Error("Method not implemented.");
  }
  async createUser(user: InsertUser): Promise<User> {
    //Implementation for creating a user in the database. Implementation needed.
    throw new Error("Method not implemented.");
  }
  async createNewsletter(newsletter: InsertNewsletter): Promise<Newsletter> {
    const [newNewsletter] = await db.insert(newsletters).values(newsletter).returning();
    return newNewsletter;
  }

  async getNewsletters(): Promise<Newsletter[]> {
    return await db.select().from(newsletters).orderBy(newsletters.createdAt);
  }

  async deleteNewsletter(id: number): Promise<void> {
    await db.delete(newsletters).where(eq(newsletters.id, id));
  }

  async getAdminByUsername(username: string): Promise<Admin | undefined> {
    const [admin] = await db.select().from(admins).where(eq(admins.username, username));
    return admin;
  }

  async verifyAdmin(username: string, password: string): Promise<boolean> {
    const admin = await this.getAdminByUsername(username);
    if (!admin) return false;
    return await bcrypt.compare(password, admin.password);
  }

  // Initialize the admin account
  async initializeAdmin() {
    const existingAdmin = await this.getAdminByUsername("khadishame");
    if (!existingAdmin) {
      const hashedPassword = await bcrypt.hash("AzizlovesKhadisha", 10);
      await db.insert(admins).values({
        username: "khadishame",
        password: hashedPassword
      });
    }
  }
}

export const storage = new DatabaseStorage();
// Initialize admin account
storage.initializeAdmin().catch(console.error);

import { users, type User, type InsertUser } from "@shared/schema";