import Image from 'next/image';
import Link from 'next/link';
import React from 'react';

const BlogCard = ({
	data,
	classes = 'grid grid-cols-1 gap-[1.875rem] sm:grid-cols-2 md:grid-cols-3',
}) => {
	return (
		<>
			<div className={classes}>
				{data.map((item) => {
					const {id, title, content, slug, image} = item;
					// const link = image.split("/").slice(3).toString().replace(".jpg", "");
					return (
						<article key={id}>
							<Link href={`/blog/detay/${slug}`}>
								<div className="rounded-2xl overflow-hidden transition-shadow hover:shadow-lg">
									<figure className="group overflow-hidden ">

										<Image
											width={370}
											height={200}
											src={'https://cdn.tevkilapp.com/' + image}
											alt={title}
											className="h-60 w-full object-fill transition-transform duration-[1600ms] will-change-transform group-hover:scale-105 "
										/>

									</figure>

									{/* <!-- Body --> */}
									<div className="dark:border-jacarta-600 dark:bg-jacarta-700 border-jacarta-100 rounded-b-[1.25rem] border border-t-0 bg-white p-[10%]">
										{/* <!-- Meta --> */}
										<h2 className="font-display text-jacarta-700 dark:hover:text-accent hover:text-accent mb-4 text-xl dark:text-white">
											{title}
										</h2>
										<p className="dark:text-jacarta-200 mb-8" dangerouslySetInnerHTML={{__html: content}}></p>
									</div>
								</div>
							</Link>
						</article>
					);
				})}
			</div>
		</>
	);
};

export default BlogCard;
