'use server';

/**
 * @fileOverview A semantic chat search AI agent.
 *
 * - semanticChatSearch - A function that handles the semantic chat search process.
 * - SemanticChatSearchInput - The input type for the semanticChatSearch function.
 * - SemanticChatSearchOutput - The return type for the semanticChatSearch function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const SemanticChatSearchInputSchema = z.object({
  query: z.string().describe('The semantic search query.'),
  chatHistory: z.array(z.string()).describe('The chat history to search through.'),
});
export type SemanticChatSearchInput = z.infer<typeof SemanticChatSearchInputSchema>;

const SemanticChatSearchOutputSchema = z.object({
  relevantChats: z.array(z.string()).describe('The relevant chat messages found based on the semantic search query.'),
});
export type SemanticChatSearchOutput = z.infer<typeof SemanticChatSearchOutputSchema>;

export async function semanticChatSearch(input: SemanticChatSearchInput): Promise<SemanticChatSearchOutput> {
  return semanticChatSearchFlow(input);
}

const prompt = ai.definePrompt({
  name: 'semanticChatSearchPrompt',
  input: {schema: SemanticChatSearchInputSchema},
  output: {schema: SemanticChatSearchOutputSchema},
  prompt: `You are an AI assistant helping users search their chat history semantically.

  Given the following search query and chat history, identify the chat messages that are most relevant to the query, even if they don't contain the exact words used in the query.

  Return only the relevant chat messages in the relevantChats array.

  Search Query: {{{query}}}

  Chat History:
  {{#each chatHistory}}
  - {{{this}}}
  {{/each}}`,
});

const semanticChatSearchFlow = ai.defineFlow(
  {
    name: 'semanticChatSearchFlow',
    inputSchema: SemanticChatSearchInputSchema,
    outputSchema: SemanticChatSearchOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
