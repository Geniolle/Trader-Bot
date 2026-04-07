export interface ProviderListResponse {
    providers: Array<{
        id: string;
        name: string;
        url: string;
        // Add other fields as needed
    }>; 
}