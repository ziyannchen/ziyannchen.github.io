require "active_support/all"
require 'net/http'
require 'json'
require 'uri'

module Helpers
  extend ActiveSupport::NumberHelper
end

module Jekyll
  class GitHubStarsTag < Liquid::Tag
    Stars = { }

    def initialize(tag_name, params, tokens)
      super
      @github_repo = params.strip
    end

    def render(context)
      github_repo = context[@github_repo.strip]
      
      # Extract owner and repo from github_repo
      # Expected format: "owner/repo" or full GitHub URL
      if github_repo.include?('github.com')
        # Extract from URL like "https://github.com/owner/repo"
        repo_path = github_repo.split('github.com/').last.split('/')[0..1].join('/')
      else
        # Assume it's already in "owner/repo" format
        repo_path = github_repo
      end

      api_url = "https://api.github.com/repos/#{repo_path}"

      begin
        # If the star count has already been fetched, return it
        if GitHubStarsTag::Stars[repo_path]
          return GitHubStarsTag::Stars[repo_path]
        end

        # Sleep for a random amount of time to avoid being rate limited
        sleep(rand(0.5..1.5))

        # Fetch the repository data from GitHub API
        uri = URI(api_url)
        http = Net::HTTP.new(uri.host, uri.port)
        http.use_ssl = true
        
        request = Net::HTTP::Get.new(uri.request_uri)
        request['User-Agent'] = "Jekyll-Site/1.0"
        
        response = http.request(request)
        
        if response.code == '200'
          data = JSON.parse(response.body)
          star_count = data['stargazers_count'].to_i
        else
          puts "GitHub API returned status: #{response.code} for #{repo_path}"
          star_count = 0
        end

        # Format the star count for readability
        star_count = Helpers.number_to_human(star_count, format: '%n%u', precision: 2, units: { thousand: 'K', million: 'M', billion: 'B' })

      rescue Exception => e
        # Handle any errors that may occur during fetching
        star_count = "N/A"

        # Print the error message including the exception class and message
        puts "Error fetching star count for #{repo_path}: #{e.class} - #{e.message}"
      end

      GitHubStarsTag::Stars[repo_path] = star_count
      return "#{star_count}"
    end
  end
end

Liquid::Template.register_tag('github_stars', Jekyll::GitHubStarsTag)