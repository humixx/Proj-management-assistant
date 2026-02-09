'use client';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface NotesState {
  notes: string;
  setNotes: (text: string) => void;
  clearNotes: () => void;
}

export const useNotesStore = create<NotesState>()(
  persist(
    (set) => ({
      notes: '',
      setNotes: (text: string) => set({ notes: text }),
      clearNotes: () => set({ notes: '' }),
    }),
    {
      name: 'notes-store',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
