import Image from "next/image";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select';


export default function Home() {
  return (
    <div className="min-h-screen bg-white font-sans antialiased">
      <header className="flex justify-between items-center px-8 py-4 border-b">
        <div className="font-bold text-xl">Operation Autopilot</div>
        <nav className="flex items-center space-x-4">
          <a href="#" className="text-sm hover:text-gray-800">Sign in</a>
          <Button variant="outline" className="bg-purple-200 text-black">Contact sales</Button>
        </nav>
      </header>

      <main className="max-w-3xl mx-auto text-center py-20 px-4">
        <p className="text-sm text-yellow-700 uppercase font-semibold mb-4">Calculator</p>
        <h1 className="text-5xl font-semibold tracking-tight mb-6">
          Janitorial Labor Costs Calculator
        </h1>
        <p className="text-gray-700 text-lg mb-8">
          Discover exactly how much your business is losing or saving due to janitorial labor shortages, using accurate market data collected from job platforms.
        </p>
        <a href="#" className="text-black underline hover:text-gray-700">
          Read more about why we created this calculator
        </a>

        <Card className="mt-[100px] mb-8">
          <CardHeader>
            <CardTitle>Janitorial Labor Cost Calculator</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4 text-sm text-gray-700">
              Enter your company's hourly rate and average weekly hours to calculate your annual janitorial labor cost.
            </p>
            <div className="flex gap-4 items-center">
              <Input type="number" step="0.01" placeholder="Hourly Rate ($)" />
              <Input type="number" step="0.01" placeholder="Weekly Hours" />
              <Button className="bg-black text-white">Calculate</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Explore the Data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="mb-4">
              <label className="block text-sm mb-2">Select a dataset</label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Default" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default</SelectItem>
                  <SelectItem value="janitors">Janitors</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="border border-gray-200 rounded p-6 text-center">
              <p className="text-gray-400">Chart will display here</p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}