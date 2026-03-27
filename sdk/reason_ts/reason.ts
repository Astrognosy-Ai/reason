export interface ReasonArtifact { /* same shape as Python */ }

export class ReasonClient {
  private registryUrl = "https://registry.reason.pub/v1";

  async resolve(address: string): Promise<ReasonArtifact> {
    const res = await fetch(`${this.registryUrl}/resolve?address=${address}`);
    return res.json();
  }
  // buildTokenizedCorpus, submitSelfInitiated, compare... (mirrors Python)
}
