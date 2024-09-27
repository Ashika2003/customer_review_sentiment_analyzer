from django.shortcuts import render
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ReviewFileSerializer
from groq import Groq
import os
import time
from django.conf import settings

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)
# Create your views here.
def analyze_sentiment(review):
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": review}],
                model="llama3-8b-8192"
            )
            sentiment = chat_completion.choices[0].message.content
            
            # Map sentiment to positive, negative, neutral
            if 'positive' in sentiment.lower():
                return {"positive": 1, "negative": 0, "neutral": 0}
            elif 'negative' in sentiment.lower():
                return {"positive": 0, "negative": 1, "neutral": 0}
            else:
                return {"positive": 0, "negative": 0, "neutral": 1}
        
        except Exception as e:
            return {"error": str(e)}
        




class SentimentAnalysisView(APIView):
    serializer_class=ReviewFileSerializer
    def post(self, request, *args, **kwargs):
        serializer = ReviewFileSerializer(data=request.data)
        
        if serializer.is_valid():
            file = serializer.validated_data['file']
            
            # Read file based on extension
            try:
                if file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                    
                else:
                    df = pd.read_csv(file)
                
                # Check if 'Review' column exists
                if 'Review' not in df.columns:
                    return Response({"error": "File must contain a 'Review' column."}, status=status.HTTP_400_BAD_REQUEST)
                
                reviews = df['Review'].dropna().tolist()  # Extract reviews
                
                # Analyze sentiment for each review
                results = []  # Initialize an empty list

# Iterate over each review and analyze sentiment
                for review in reviews:
                    sentiment_result = analyze_sentiment(review)
                    
                    print(sentiment_result)
                    results.append(sentiment_result)  

                # Print the results
                
                return Response({"sentiments": results}, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)